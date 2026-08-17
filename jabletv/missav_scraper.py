"""Scraper for missav.ws — extracts video metadata and m3u8 URL.

URL pattern: https://missav.ws/<category>/<video-slug>/
Example: https://missav.ws/dm26/abp-664-uncensored-leak

The m3u8 URL is obfuscated inside a JavaScript packed (eval'd) script.
This module decodes it using the same unpacking strategy as the JS packer.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from urllib.parse import unquote

import httpx

from .utils import rotating_ua, CFFI_PROFILES

logger = logging.getLogger(__name__)

MISSAV_BASE = "https://missav.ws"

# Pattern to extract the per-variant URL assignment from decoded JS
# e.g. source='https://...'; source842='https://...'; source1280='https://...'
SOURCE_ASSIGN_PATTERN = re.compile(
    r"(?:var\s+)?([a-zA-Z]\w*)\s*=\s*'([^']+)'"
)

# Domains we accept as missav
MISSAV_DOMAINS = ("missav.ws", "missav.com", "msav.ws")


@dataclass
class MissavVideoInfo:
    code: str = ""
    title: str = ""
    full_title: str = ""
    m3u8_url: str = ""
    thumbnail: str = ""
    actresses: list[str] = field(default_factory=list)
    video_id: str = ""

    @property
    def output_filename(self) -> str:
        from .utils import sanitize_filename

        actresses_str = " - ".join(self.actresses) if self.actresses else ""
        parts = [self.code]
        if actresses_str:
            parts.append(actresses_str)
        return sanitize_filename(" - ".join(parts)) + ".mp4"


def is_missav_url(url: str) -> bool:
    """Check if a URL belongs to a supported missav domain."""
    for domain in MISSAV_DOMAINS:
        if domain in url:
            return True
    return False


# ---------------------------------------------------------------------------
# JS Packer decoder
# ---------------------------------------------------------------------------

def _unpack_js_packed(packed_str: str, words: list[str]) -> str:
    """Decode a JavaScript packed string (the "p.a.c.k.e" algorithm).

    In the packed representation, each distinct word-like token is replaced by
    its index (as a base-N string) in the word array.  We reverse it by
    replacing each base-36 word back with the word from the array.

    Args:
        packed_str: The obfuscated string (e.g. "f='8://7.6/5-4-3-2-1/e.0'")
        words: The word list (split from the '|' separated list).

    Returns:
        The decoded JavaScript snippet.
    """
    # Build reverse mapping: base-36 string -> word
    lookup: dict[str, str] = {}
    for idx, w in enumerate(words):
        key = _to_base36(idx)
        lookup[key] = w

    # Replace each base-36 token with its word
    # Tokens are alphanumeric, separated by non-alphanumeric chars
    result_parts: list[str] = []
    buf: list[str] = []
    for ch in packed_str:
        if ch.isalnum():
            buf.append(ch)
        else:
            if buf:
                token = "".join(buf)
                result_parts.append(lookup.get(token, token))
                buf = []
            result_parts.append(ch)
    if buf:
        token = "".join(buf)
        result_parts.append(lookup.get(token, token))

    return "".join(result_parts)


def _to_base36(n: int) -> str:
    """Convert integer to base-36 string (0-9a-z)."""
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    if n < 36:
        return chars[n]
    result: list[str] = []
    while n > 0:
        result.append(chars[n % 36])
        n //= 36
    return "".join(reversed(result))


def _extract_m3u8_from_eval(html: str) -> str:
    """Find and decode the packed eval that contains m3u8 URLs.

    The eval has nested braces so we use brace counting to extract
    the parameter list instead of a naive regex.

    Returns the master playlist URL (the one ending in 'playlist.m3u8'
    or the highest-quality variant URL).
    """
    # Find 'eval(function(p,a,c,k,e,d)'
    marker = "eval(function(p,a,c,k,e,d)"
    eval_idx = html.find(marker)
    if eval_idx < 0:
        logger.debug("No packed eval found in missav page")
        return ""

    # From the marker, find the matching brace pair { ... }
    # Then the params follow as }(...)
    brace_start = html.find("{", eval_idx)
    if brace_start < 0:
        return ""

    # Count braces to find the matching }
    depth = 0
    func_end = brace_start
    for i in range(brace_start, len(html)):
        if html[i] == "{":
            depth += 1
        elif html[i] == "}":
            depth -= 1
            if depth == 0:
                func_end = i + 1
                break
    else:
        return ""  # unbalanced braces

    # Now extract the parameters: }('...', ...))
    # The params may contain nested parens (e.g. split('|')), so use
    # parenthesis counting to extract the full argument list.
    search_start = max(0, func_end - 5)
    chunk = html[search_start:search_start + 500]
    # Find the opening paren right after the closing brace
    open_idx = chunk.find("(")
    if open_idx < 0:
        return ""
    depth = 0
    close_idx = open_idx
    for i in range(open_idx, len(chunk)):
        if chunk[i] == "(":
            depth += 1
        elif chunk[i] == ")":
            depth -= 1
            if depth == 0:
                close_idx = i
                break
    else:
        return ""  # unbalanced parens

    params = chunk[open_idx + 1:close_idx]

    # Extract the packed string (first quoted parameter).
    # The string may contain escaped single quotes (\'), so we find
    # the first unescaped '...', pair that marks the end.
    packed_str = ""
    if params.startswith("'"):
        # Walk through finding the closing ' that is not escaped
        j = 1
        while j < len(params):
            if params[j] == "'" and (j == 0 or params[j - 1] != "\\"):
                # This is the closing quote, but only if followed by ','
                if j + 1 < len(params) and params[j + 1] == ",":
                    # Extract the raw string content, removing escape backslashes
                    raw = params[1:j]
                    packed_str = raw.replace("\\'", "'").replace("\\/", "/")
                    break
            j += 1

    if not packed_str:
        return ""

    # Extract the word list - the long 'word0|word1|...' string
    word_list_match = re.search(r"'((?:[^']+\|)+[^']+)'", params)
    if not word_list_match:
        return ""
    words = word_list_match.group(1).split("|")

    decoded = _unpack_js_packed(packed_str, words)
    logger.debug("Decoded JS snippet: %s", decoded[:200])

    # Parse the decoded assignments
    sources: dict[str, str] = {}
    for var_name, url in SOURCE_ASSIGN_PATTERN.findall(decoded):
        url = url.replace("\\/", "/").replace("\\u0026", "&")
        sources[var_name] = url

    # Priority: source (playlist.m3u8) > source1280 > source842
    for key in ("source", "source1280", "source842"):
        if key in sources:
            return sources[key]

    # Fallback: return any URL that contains .m3u8
    for url in sources.values():
        if ".m3u8" in url:
            return url

    return ""


# ---------------------------------------------------------------------------
# Metadata extraction
# ---------------------------------------------------------------------------

def _extract_full_title(html: str) -> str:
    match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback to og:title
    match = re.search(
        r'<meta\s+property="og:title"\s+content="([^"]+)"', html
    )
    if match:
        return match.group(1).strip()
    return ""


def _extract_code(full_title: str) -> str:
    match = re.match(r"([A-Z]+-\d+)", full_title)
    return match.group(1) if match else ""


def _extract_actresses(html: str) -> list[str]:
    """Extract actress names from /actresses/ URL slugs."""
    slugs = re.findall(r'/actresses/([^"\'/]+)', html)
    names: list[str] = []
    seen: set[str] = set()
    for slug in slugs:
        try:
            name = unquote(slug)
        except Exception:
            name = slug
        # Skip non-name slugs like "ranking"
        if name in seen or name in ("ranking",):
            continue
        seen.add(name)
        # Keep Japanese/Chinese characters (full-width) or valid unicode names
        if re.search(r"[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]", name):
            names.append(name)
    return names


def _extract_thumbnail(html: str) -> str:
    match = re.search(
        r'<meta\s+property="og:image"\s+content="([^"]+)"', html
    )
    return match.group(1) if match else ""


def _extract_video_id(html: str) -> str:
    """Extract the internal video/item ID if present."""
    # From window.dataLayer push
    match = re.search(r'dvd_id:\s*["\']([^"\']+)["\']', html)
    if match:
        return match.group(1)

    # From API call path: /api/items/<id>/...
    match = re.search(r'/api/items/([a-zA-Z0-9]+)/', html)
    if match:
        return match.group(1)

    # From URL path (last non-empty segment)
    match = re.search(r'missav\.\w+/[^/]+/([^/?#]+)', html)
    if match:
        from urllib.parse import urlparse, parse_qs
        # We don't have the URL here, so just return the slug
        pass

    return ""


# ---------------------------------------------------------------------------
# Page fetching
# ---------------------------------------------------------------------------

def _fetch_page(url: str) -> str:
    """Fetch a missav.ws page, rotating curl_cffi impersonation profiles
    then falling back to plain httpx."""
    headers = {
        "User-Agent": rotating_ua(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
        "Referer": f"{MISSAV_BASE}/",
    }

    try:
        from curl_cffi import requests as curl_requests  # type: ignore[import-untyped]
    except ImportError:
        curl_requests = None
        logger.debug("curl_cffi not available, falling back to httpx")

    if curl_requests is not None:
        # Let curl_cffi set a UA matching the impersonated TLS fingerprint;
        # a mismatched UA over a fingerprint triggers Cloudflare 403s.
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


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def scrape_missav(url: str) -> MissavVideoInfo:
    """Scrape a missav.ws video page for metadata and m3u8 URL.

    Args:
        url: The full missav.ws video URL.

    Returns:
        A MissavVideoInfo dataclass with extracted data.

    Raises:
        ValueError: If the URL is invalid or scraping fails.
        httpx.HTTPStatusError: On HTTP errors.
    """
    logger.info("Scraping missav URL: %s", url)

    html = _fetch_page(url)

    full_title = _extract_full_title(html)
    code = _extract_code(full_title)
    title = full_title[len(code):].strip() if full_title.startswith(code) else full_title

    m3u8_url = _extract_m3u8_from_eval(html)
    thumbnail = _extract_thumbnail(html)
    actresses = _extract_actresses(html)
    video_id = _extract_video_id(html)

    if not m3u8_url:
        logger.warning("No m3u8 URL found in missav page: %s", url)

    return MissavVideoInfo(
        code=code,
        title=title,
        full_title=full_title,
        m3u8_url=m3u8_url,
        thumbnail=thumbnail,
        actresses=actresses,
        video_id=video_id,
    )
