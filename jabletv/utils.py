import random
import unicodedata


# curl_cffi impersonation profiles verified to work with curl_cffi 0.13.
# Cloudflare intermittently flags individual TLS fingerprints, so fetchers
# rotate through these before falling back to plain httpx.
# NOTE: chrome131 was fully flagged by Cloudflare (consistent 403) and was
# replaced with chrome136 (verified 200 with curl_cffi 0.13).
CFFI_PROFILES = ["chrome120", "chrome124", "chrome136", "safari17_0", "firefox133"]


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
]


def rotating_ua() -> str:
    return random.choice(USER_AGENTS)


def sanitize_filename(name: str) -> str:
    replacements = {
        "●": "·", "・": "·", "「": "[", "」": "]", "！": "!",
        "？": "?", "（": "(", "）": ")", "、": ",",
    }
    for old, new in replacements.items():
        name = name.replace(old, new)

    safe: list[str] = []
    for c in name:
        if c.isalnum() or c in " _-.,()[]!@#$%^&+='~`?:":
            safe.append(c)
        elif ord(c) > 127 and not unicodedata.category(c).startswith("C"):
            safe.append(c)

    name = "".join(safe).strip()[:80]
    return name if name else "untitled"
