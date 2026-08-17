from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from jabletv.downloader import (
    decrypt_segment,
    parse_m3u8_content,
    resolve_master_m3u8,
    verify_media_file,
    download,
)
from jabletv.scraper import VideoInfo


class TestDecryptSegment:
    def test_aes_decrypt(self) -> None:
        key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
        iv = bytes(16)

        plaintext = b"Hello AES test!!"
        pad_len = 16 - (len(plaintext) % 16)
        padded = plaintext + bytes([pad_len] * pad_len)

        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded) + encryptor.finalize()

        result = decrypt_segment(ciphertext, key, iv)
        assert result == plaintext


class TestResolveMasterM3U8:
    def test_resolves_variant(self) -> None:
        m3u8_content = (
            "#EXTM3U\n"
            "#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=640x360\n"
            "https://cdn.example.com/360p.m3u8\n"
            "#EXT-X-STREAM-INF:BANDWIDTH=4000000,RESOLUTION=1920x1080\n"
            "https://cdn.example.com/1080p.m3u8\n"
        )

        with patch("jabletv.downloader._fetch_with_cffi", return_value=m3u8_content):
            result = resolve_master_m3u8("https://cdn.example.com/master.m3u8")
            assert result == "https://cdn.example.com/1080p.m3u8"

    def test_returns_same_if_not_variant(self) -> None:
        m3u8_content = (
            "#EXTM3U\n"
            "#EXTINF:10.0,\n"
            "seg-0.ts\n"
            "#EXT-X-ENDLIST\n"
        )

        with patch("jabletv.downloader._fetch_with_cffi", return_value=m3u8_content):
            result = resolve_master_m3u8("https://cdn.example.com/video.m3u8")
            assert result == "https://cdn.example.com/video.m3u8"


class TestParseM3U8Content:
    def test_parses_segments(self, unencrypted_m3u8: str) -> None:
        with patch("jabletv.downloader._fetch_with_cffi", return_value=unencrypted_m3u8):
            segments, key, iv, seq = parse_m3u8_content(
                "https://cdn.example.com/video.m3u8"
            )

        assert len(segments) == 3
        assert all("cdn.example.com" in s for s in segments)
        assert key is None
        assert iv is None
        assert seq == 0

    def test_parses_encrypted_segments(self, encrypted_m3u8: str) -> None:
        key_bytes = bytes.fromhex("000102030405060708090a0b0c0d0e0f")

        def mock_fetch(url: str, headers=None):
            if "key.bin" in url:
                return key_bytes
            return encrypted_m3u8

        with patch("jabletv.downloader._fetch_with_cffi", side_effect=lambda url, headers=None: encrypted_m3u8 if "m3u8" in url else ""):
            with patch("jabletv.downloader._fetch_binary_with_cffi", return_value=key_bytes):
                segments, key, iv, seq = parse_m3u8_content(
                    "https://cdn.example.com/encrypted.m3u8"
                )

        assert len(segments) == 2
        assert key == key_bytes
        assert iv is not None
        assert len(iv) == 16


class TestVerifyMediaFile:
    def test_valid_file(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test.mp4"
        test_file.write_bytes(b"\x00" * 1024)

        with patch("subprocess.run") as mock_run:
            mock_proc = Mock()
            mock_proc.returncode = 0
            mock_run.return_value = mock_proc
            ok, msg = verify_media_file(str(test_file))

        assert ok
        assert msg == ""

    def test_missing_file(self, tmp_path: Path) -> None:
        ok, msg = verify_media_file(str(tmp_path / "nonexistent.mp4"))
        assert not ok

    def test_ffprobe_failure(self, tmp_path: Path) -> None:
        test_file = tmp_path / "bad.mp4"
        test_file.write_bytes(b"\x00" * 100)

        with patch("subprocess.run") as mock_run:
            mock_proc = Mock()
            mock_proc.returncode = 1
            mock_proc.stderr = "Invalid data"
            mock_run.return_value = mock_proc
            ok, msg = verify_media_file(str(test_file))

        assert not ok
        assert "Invalid data" in msg


class TestFetchRetry:
    def test_fetch_with_cffi_retries_then_succeeds_via_httpx(self) -> None:
        """A transient 403 on both transports must be retried with a fresh
        UA rather than failing the whole download."""
        import httpx as httpx_mod

        from jabletv import downloader as dl_mod

        class FakeClient:
            def __init__(self, responses):
                self.responses = list(responses)

            def get(self, url, headers=None):
                return self.responses.pop(0)

            def close(self):
                pass

        def make_resp(status: int, text: str = "") -> httpx_mod.Response:
            return httpx_mod.Response(
                status,
                request=httpx_mod.Request("GET", "https://cdn.example.com/v.m3u8"),
                text=text,
            )

        def cffi_403(url, headers=None, **kwargs):
            raise Exception("HTTP Error 403: ")

        fake = FakeClient([
            make_resp(403),
            make_resp(200, "#EXTM3U\n#EXT-X-ENDLIST\n"),
        ])

        with patch("curl_cffi.requests.get", side_effect=cffi_403):
            with patch.object(dl_mod.httpx, "Client", return_value=fake):
                with patch.object(dl_mod.time, "sleep"):
                    result = dl_mod._fetch_with_cffi(
                        "https://cdn.example.com/v.m3u8"
                    )

        assert "#EXT-X-ENDLIST" in result

    def test_fetch_raises_after_exhausting_retries(self) -> None:
        import httpx as httpx_mod

        from jabletv import downloader as dl_mod

        class FakeClient:
            def get(self, url, headers=None):
                return httpx_mod.Response(
                    403,
                    request=httpx_mod.Request("GET", url),
                )

            def close(self):
                pass

        def cffi_403(url, headers=None, **kwargs):
            raise Exception("HTTP Error 403: ")

        with patch("curl_cffi.requests.get", side_effect=cffi_403):
            with patch.object(dl_mod.httpx, "Client", return_value=FakeClient()):
                with patch.object(dl_mod.time, "sleep"):
                    with pytest.raises(httpx_mod.HTTPStatusError):
                        dl_mod._fetch_with_cffi("https://cdn.example.com/v.m3u8")


class TestDownload:
    def test_no_m3u8_url_raises(self) -> None:
        video = VideoInfo(code="TEST", m3u8_url="")
        with pytest.raises(ValueError, match="no m3u8 url"):
            download(video)

    def test_no_segments_raises(self, tmp_path: Path) -> None:
        video = VideoInfo(code="TEST", m3u8_url="https://cdn.example.com/video.m3u8")

        with patch("jabletv.downloader.resolve_master_m3u8",
                   return_value="https://cdn.example.com/video.m3u8"):
            with patch("jabletv.downloader.parse_m3u8_content",
                       return_value=([], None, None, 0)):
                with pytest.raises(ValueError, match="no segments"):
                    download(video, output_dir=str(tmp_path))

    def test_skips_if_already_downloaded(self, tmp_path: Path) -> None:
        video = VideoInfo(code="TEST", m3u8_url="https://cdn.example.com/video.m3u8")
        output_file = tmp_path / "TEST.mp4"
        output_file.write_bytes(b"x" * (2 * 1024 * 1024))

        with patch("jabletv.downloader.VideoInfo.output_filename",
                   new_callable=lambda: property(lambda self: "TEST.mp4")):
            result = download(video, output_dir=str(tmp_path))

        assert result == output_file

    def test_progress_callbacks_fire(self, tmp_path: Path) -> None:
        video = VideoInfo(code="TEST", m3u8_url="https://cdn.example.com/video.m3u8")

        output_file = tmp_path / "TEST.mp4"
        output_file.write_bytes(b"\x00" * (2 * 1024 * 1024))

        progress_calls: list[tuple] = []

        def progress_cb(pct, speed, eta, status):
            progress_calls.append((pct, status))

        with patch("jabletv.downloader.VideoInfo.output_filename",
                   new_callable=lambda: property(lambda self: "TEST.mp4")):
            result = download(video, output_dir=str(tmp_path), progress_callback=progress_cb)

        assert result == output_file
        assert len(progress_calls) > 0
        assert progress_calls[0][1] == "Already downloaded"
