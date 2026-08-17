from __future__ import annotations

import logging
import os
import shutil
import time
import subprocess
import threading
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx
import m3u8

from .scraper import VideoInfo
from .utils import rotating_ua, CFFI_PROFILES

logger = logging.getLogger(__name__)

CFFI_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://jable.tv/",
    "Origin": "https://jable.tv",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
}


def _fetch_with_cffi(url: str, headers: dict | None = None, retries: int = 3) -> str:
    """Fetch a URL using curl_cffi impersonation, falling back to httpx.

    CDNs intermittently 403 a request and serve the same URL on retry
    (with a fresh UA), so transient failures are retried with backoff.
    """
    req_headers = dict(CFFI_HEADERS)
    if headers:
        req_headers.update(headers)
    else:
        req_headers["User-Agent"] = rotating_ua()

    # Let curl_cffi supply a UA matching the impersonated TLS fingerprint.
    # A mismatched UA over a browser fingerprint triggers Cloudflare 403s.
    cffi_headers = {k: v for k, v in req_headers.items() if k != "User-Agent"}
    httpx_headers = dict(req_headers)
    httpx_headers.setdefault("User-Agent", rotating_ua())

    last_exc: Exception | None = None
    for attempt in range(retries):
        if attempt:
            httpx_headers["User-Agent"] = rotating_ua()
            time.sleep(min(2 ** attempt, 8))
        profile = CFFI_PROFILES[attempt % len(CFFI_PROFILES)]

        try:
            from curl_cffi import requests as curl_requests
            resp = curl_requests.get(
                url,
                headers=cffi_headers,
                impersonate=profile,
                timeout=30,
            )
            resp.raise_for_status()
            return resp.text
        except ImportError:
            pass
        except Exception as exc:
            last_exc = exc
            logger.warning("curl_cffi(%s) failed for %s: %s", profile, url, exc)

        client = httpx.Client(timeout=30.0, follow_redirects=True)
        try:
            resp = client.get(url, headers=httpx_headers)
            resp.raise_for_status()
            return resp.text
        except Exception as exc:
            last_exc = exc
            logger.warning("httpx failed for %s: %s", url, exc)
        finally:
            client.close()

    if last_exc:
        raise last_exc
    raise RuntimeError(f"request failed: {url}")


def _fetch_binary_with_cffi(url: str, headers: dict | None = None, retries: int = 3) -> bytes:
    """Fetch binary content using curl_cffi impersonation, falling back to httpx.

    Same transient-403 retry behavior as :func:`_fetch_with_cffi`.
    """
    req_headers = dict(CFFI_HEADERS)
    if headers:
        req_headers.update(headers)
    else:
        req_headers["User-Agent"] = rotating_ua()

    # Same UA/fingerprint matching rationale as :func:`_fetch_with_cffi`.
    cffi_headers = {k: v for k, v in req_headers.items() if k != "User-Agent"}
    httpx_headers = dict(req_headers)
    httpx_headers.setdefault("User-Agent", rotating_ua())

    last_exc: Exception | None = None
    for attempt in range(retries):
        if attempt:
            httpx_headers["User-Agent"] = rotating_ua()
            time.sleep(min(2 ** attempt, 8))
        profile = CFFI_PROFILES[attempt % len(CFFI_PROFILES)]

        try:
            from curl_cffi import requests as curl_requests
            resp = curl_requests.get(
                url,
                headers=cffi_headers,
                impersonate=profile,
                timeout=30,
            )
            resp.raise_for_status()
            return resp.content
        except ImportError:
            pass
        except Exception as exc:
            last_exc = exc
            logger.warning("curl_cffi(%s) failed for key %s: %s", profile, url, exc)

        client = httpx.Client(timeout=30.0, follow_redirects=True)
        try:
            resp = client.get(url, headers=httpx_headers)
            resp.raise_for_status()
            return resp.content
        except Exception as exc:
            last_exc = exc
            logger.warning("httpx failed for key %s: %s", url, exc)
        finally:
            client.close()

    if last_exc:
        raise last_exc
    raise RuntimeError(f"request failed: {url}")


def parse_m3u8_content(m3u8_url: str, headers: dict | None = None) -> tuple[list[str], bytes | None, bytes | None, int]:
    merged_headers = dict(CFFI_HEADERS)
    if headers:
        merged_headers.update(headers)
    else:
        merged_headers["User-Agent"] = rotating_ua()

    text = _fetch_with_cffi(m3u8_url, merged_headers)
    playlist = m3u8.loads(text, uri=m3u8_url)

    segments: list[str] = []
    for seg in playlist.segments:
        seg_url = urljoin(m3u8_url, seg.uri)
        segments.append(seg_url)

    key_data: bytes | None = None
    iv: bytes | None = None
    if playlist.keys and playlist.keys[0]:
        key_obj = playlist.keys[0]
        key_url = urljoin(m3u8_url, key_obj.uri) if key_obj.uri else None
        if key_url:
            key_data = _fetch_binary_with_cffi(key_url, merged_headers)

        if key_obj.iv:
            iv_hex = key_obj.iv.lstrip("0x")
            iv = bytes.fromhex(iv_hex.rjust(32, "0"))

    media_sequence = playlist.media_sequence or 0

    return segments, key_data, iv, media_sequence


def decrypt_segment(data: bytes, key: bytes, iv: bytes) -> bytes:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(data) + decryptor.finalize()
    pad_len = decrypted[-1]
    if 0 < pad_len <= 16:
        decrypted = decrypted[:-pad_len]
    return decrypted


def resolve_master_m3u8(m3u8_url: str, headers: dict | None = None) -> str:
    merged_headers = dict(CFFI_HEADERS)
    if headers:
        merged_headers.update(headers)
    else:
        merged_headers["User-Agent"] = rotating_ua()

    text = _fetch_with_cffi(m3u8_url, merged_headers)
    playlist = m3u8.loads(text, uri=m3u8_url)

    if not playlist.is_variant:
        return m3u8_url

    best = max(playlist.playlists, key=lambda p: p.stream_info.bandwidth or 0)
    variant_url = urljoin(m3u8_url, best.uri)
    return variant_url


def verify_media_file(path: str) -> tuple[bool, str]:
    if not os.path.exists(path) or os.path.getsize(path) <= 0:
        return False, "file missing or empty"
    try:
        proc = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, timeout=30,
        )
        if proc.returncode != 0:
            return False, f"ffprobe failed: {(proc.stderr or proc.stdout or '').strip()}"
        return True, ""
    except Exception as e:
        return False, f"ffprobe exception: {e}"


def _noop_progress(pct: int, speed: str, eta: str, status: str) -> None:
    pass


def _find_ffmpeg() -> str:
    candidates = [
        "ffmpeg",
        os.path.expanduser("~/miniconda3/bin/ffmpeg"),
        os.path.expanduser("~/anaconda3/bin/ffmpeg"),
        "/opt/homebrew/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
    ]
    for path_ in candidates:
        if shutil.which(path_):
            return path_
    msg = (
        "ffmpeg not found. Install it:\n"
        "  macOS:  brew install ffmpeg\n"
        "  Linux:  sudo apt install ffmpeg  or  sudo dnf install ffmpeg\n"
        "  conda:  conda install ffmpeg"
    )
    raise RuntimeError(msg)


def download(
    video: VideoInfo,
    output_dir: Optional[str] = None,
    progress_callback: Optional[Callable] = None,
    concurrency: int = 8,
    referer: Optional[str] = None,
) -> Path:
    if progress_callback is None:
        progress_callback = _noop_progress
    if output_dir is None:
        output_dir = "."

    if not video.m3u8_url:
        logger.error("No m3u8 URL for video: %s", video.code)
        raise ValueError("no m3u8 url")

    logger.info("Starting download: %s", video.code)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / video.output_filename

    if output_path.exists() and output_path.stat().st_size > 1024 * 1024:
        logger.info("Already downloaded: %s", output_path)
        progress_callback(100, "done", "", "Already downloaded")
        return output_path

    progress_callback(0, "", "", "Resolving playlist...")

    # Use a site-appropriate referer (jable.tv default, overridable for other sites)
    site_referer = referer or "https://jable.tv/"
    from urllib.parse import urlparse
    parsed = urlparse(site_referer)
    site_origin = f"{parsed.scheme}://{parsed.netloc}"

    headers = {
        "User-Agent": rotating_ua(),
        "Referer": site_referer,
        "Origin": site_origin,
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    variant_url = resolve_master_m3u8(video.m3u8_url, headers)
    segments, key_data, iv, media_sequence = parse_m3u8_content(variant_url, headers)

    if not segments:
        raise ValueError("no segments found in playlist")

    total = len(segments)
    progress_callback(0, "", "", f"Downloading {total} segments...")

    parts_dir = out_dir / f".{video.code}_parts"
    parts_dir.mkdir(exist_ok=True)

    temp_ts = out_dir / f".{video.code}_merged.ts"
    temp_mp4 = out_dir / f".{video.code}_temp.mp4"

    completed_lock = threading.Lock()
    start_time = time.time()
    last_update = time.time()

    def part_path(idx: int) -> Path:
        return parts_dir / f"{idx:06d}.ts"

    def download_seg(idx: int, url: str) -> tuple[int, bool, str]:
        target = part_path(idx)
        if target.exists() and target.stat().st_size > 0:
            return idx, True, "cached"

        seg_headers = dict(headers)
        seg_headers["User-Agent"] = rotating_ua()

        last_err = ""
        for attempt in range(1, 4):
            try:
                data = _fetch_binary_with_cffi(url, seg_headers)

                if key_data:
                    seg_iv = iv if iv else (media_sequence + idx).to_bytes(16, byteorder="big")
                    data = decrypt_segment(data, key_data, seg_iv)

                tmp = target.with_suffix(".tmp")
                tmp.write_bytes(data)
                tmp.rename(target)
                return idx, True, ""
            except Exception as exc:
                last_err = str(exc)
                time.sleep(min(2 * attempt, 8))

        return idx, False, last_err

    try:
        existing = sum(1 for i in range(total) if part_path(i).exists() and part_path(i).stat().st_size > 0)

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = {
                executor.submit(download_seg, i, url): i
                for i, url in enumerate(segments)
                if not (part_path(i).exists() and part_path(i).stat().st_size > 0)
            }

            for future in as_completed(futures):
                idx, ok, err = future.result()
                if not ok:
                    executor.shutdown(wait=False, cancel_futures=True)
                    raise RuntimeError(f"segment {idx} download failed: {err}")

                with completed_lock:
                    existing += 1

                now = time.time()
                if now - last_update > 0.5:
                    pct = int(existing / total * 90)
                    elapsed = max(now - start_time, 0.001)
                    bytes_done = sum(
                        part_path(i).stat().st_size
                        for i in range(total)
                        if part_path(i).exists()
                    )
                    speed = bytes_done / elapsed / 1024 / 1024
                    remaining_time = (total - existing) * elapsed / max(existing, 1)
                    eta = f"{int(remaining_time // 60)}:{int(remaining_time % 60):02d}" if remaining_time > 0 else "?"
                    status = f"{existing}/{total} segments"
                    progress_callback(pct, f"{speed:.1f} MB/s", eta, status)
                    last_update = now

        missing = [i for i in range(total) if not (part_path(i).exists() and part_path(i).stat().st_size > 0)]
        if missing:
            raise RuntimeError(f"{len(missing)} segments missing: {missing[:10]}")

        progress_callback(92, "", "", "Merging TS segments...")

        with open(temp_ts, "wb") as out:
            for i in range(total):
                with open(part_path(i), "rb") as part:
                    shutil.copyfileobj(part, out, length=4 * 1024 * 1024)

        progress_callback(96, "", "", "Converting to MP4...")

        ffmpeg_bin = _find_ffmpeg()
        cmd = [
            ffmpeg_bin, "-y",
            "-i", str(temp_ts),
            "-c", "copy", "-bsf:a", "aac_adtstoasc",
            "-movflags", "+faststart",
            "-f", "mp4",
            str(temp_mp4),
        ]
        proc = subprocess.run(cmd, capture_output=True, universal_newlines=True, timeout=600)

        if proc.returncode != 0 or not temp_mp4.exists():
            raw_err = (proc.stderr or proc.stdout or "").strip()
            err_lines = raw_err.split("\n")[-5:]
            raise RuntimeError(f"ffmpeg failed: {' | '.join(err_lines)}")

        ok, verify_err = verify_media_file(str(temp_mp4))
        if not ok:
            raise RuntimeError(f"media verification failed: {verify_err}")

        temp_mp4.rename(output_path)
        logger.info("Download complete: %s", output_path)
        progress_callback(100, "done", "", "Complete!")

    finally:
        if temp_ts.exists():
            temp_ts.unlink()
        if temp_mp4.exists():
            temp_mp4.unlink()
        if parts_dir.exists():
            shutil.rmtree(parts_dir, ignore_errors=True)

    return output_path
