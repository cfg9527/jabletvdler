from __future__ import annotations

import logging
import re

import httpx
from dataclasses import dataclass, field

from .utils import rotating_ua, CFFI_PROFILES

logger = logging.getLogger(__name__)

JABLE_BASE = "https://jable.tv"
M3U8_PATTERNS = [
    r"var hlsUrl\s*=\s*'([^']+)'",
    r'var hlsUrl\s*=\s*"([^"]+)"',
    r'(https?://[^"\'<>\\]+\.m3u8[^"\'<>]*)',
]


@dataclass
class VideoInfo:
    code: str = ""
    title: str = ""
    full_title: str = ""
    actresses: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    category: str = ""
    release_date: str = ""
    views: int = 0
    thumbnail: str = ""
    m3u8_url: str = ""
    video_id: str = ""

    @property
    def output_filename(self) -> str:
        from .utils import sanitize_filename
        actresses_str = " - ".join(self.actresses) if self.actresses else ""
        parts = [self.code]
        if actresses_str:
            parts.append(actresses_str)
        return sanitize_filename(" - ".join(parts)) + ".mp4"


def _extract_m3u8(html: str) -> str:
    for pattern in M3U8_PATTERNS:
        match = re.search(pattern, html)
        if match:
            url = match.group(1)
            url = url.replace("\\/", "/").replace("\\u0026", "&")
            if url.startswith("http"):
                return url
    return ""


def _extract_video_id(html: str) -> str:
    match = re.search(r"videoId:\s*'(\d+)'", html)
    return match.group(1) if match else ""


def _extract_thumbnail(html: str) -> str:
    match = re.search(r'poster="([^"]+)"', html)
    return match.group(1) if match else ""


def _extract_actresses(html: str) -> list[str]:
    names: list[str] = []

    for match in re.finditer(
        r'<a[^>]*class="model"[^>]*href="[^"]*?/models/[^"]*">'
        r'.*?<span[^>]*title="([^"]+)"[^>]*>.*?</span>',
        html,
        re.DOTALL,
    ):
        name = match.group(1).strip()
        if name and name not in names:
            names.append(name)

    if not names:
        for match in re.finditer(
            r'<a[^>]*href="[^"]*?/models/[^"]*"[^>]*>'
            r'\s*(?:<div[^>]*>.*?</div>\s*)?<span[^>]*>([^<]+)</span>',
            html,
        ):
            name = match.group(1).strip()
            if name and name not in names:
                names.append(name)

    if not names:
        for match in re.finditer(
            r'<a[^>]*class="model"[^>]*>.*?title="([^"]+)".*?</a>',
            html,
        ):
            names.append(match.group(1).strip())
    return names


def _extract_tags(html: str) -> list[str]:
    tags: list[str] = []
    for match in re.finditer(
        r'<a[^>]*href="[^"]*?/tags/([^/"]+)/"[^>]*>([^<]+)</a>',
        html,
    ):
        tags.append(match.group(2).strip())
    return tags


def _extract_category(html: str) -> str:
    match = re.search(
        r'<a[^>]*href="[^"]*?/categories/[^/"]+/"[^>]*class="cat"[^>]*>([^<]+)</a>',
        html,
    )
    return match.group(1).strip() if match else ""


def _extract_release_date(html: str) -> str:
    match = re.search(r"上市於\s*(\d{4}-\d{2}-\d{2})", html)
    return match.group(1) if match else ""


def _extract_views(html: str) -> int:
    match = re.search(r'<span class="mr-3">\s*([\d\s,]+)\s*</span>', html)
    if match:
        return int(match.group(1).replace(" ", "").replace(",", ""))
    return 0


def _fetch_page(url: str) -> str:
    """Fetch a jable.tv page, trying curl_cffi impersonation profiles
    then plain httpx as a last resort.

    jable.tv's bot protection intermittently 403s individual TLS
    fingerprints (curl_cffi profiles) and blocks plain httpx outright,
    so we rotate through supported profiles before giving up.
    """
    headers = {
        "User-Agent": rotating_ua(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": f"{JABLE_BASE}/",
    }

    try:
        from curl_cffi import requests as curl_requests
    except ImportError:
        curl_requests = None
        logger.debug("curl_cffi not available, falling back to httpx")

    if curl_requests is not None:
        # Let curl_cffi set a UA matching the impersonated TLS fingerprint.
        # Sending a mismatched random UA (e.g. a Firefox UA over a Chrome
        # fingerprint) gets jable.tv's Cloudflare to 403 intermittently.
        cffi_headers = {k: v for k, v in headers.items() if k != "User-Agent"}
        for profile in CFFI_PROFILES:
            try:
                resp = curl_requests.get(
                    url,
                    headers=cffi_headers,
                    impersonate=profile,
                    timeout=30,
                )
                resp.raise_for_status()
                return resp.text
            except Exception as exc:
                logger.warning("curl_cffi(%s) failed for %s: %s", profile, url, exc)

    resp = httpx.get(url, headers=headers, timeout=30, follow_redirects=True)
    resp.raise_for_status()
    return resp.text


def scrape(url: str) -> VideoInfo:
    logger.info("Scraping URL: %s", url)
    try:
        html = _fetch_page(url)
    except Exception as e:
        logger.error("Failed to fetch page: %s", e)
        raise

    full_title_match = re.search(r"<h4>(.+?)</h4>", html)
    full_title = full_title_match.group(1).strip() if full_title_match else ""

    code = full_title.split(" ")[0].upper() if full_title else ""

    title = full_title[len(code):].strip() if full_title.startswith(code) else full_title

    logger.info("Scraped video: %s", code)
    return VideoInfo(
        code=code,
        title=title,
        full_title=full_title,
        actresses=_extract_actresses(html),
        tags=_extract_tags(html),
        category=_extract_category(html),
        release_date=_extract_release_date(html),
        views=_extract_views(html),
        thumbnail=_extract_thumbnail(html),
        m3u8_url=_extract_m3u8(html),
        video_id=_extract_video_id(html),
    )
