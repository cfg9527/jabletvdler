# GitHub Reference — JableTV Downloader Ecosystem Research

> Researched 2026-07-11. Top 3 starred jable.tv downloader repos on GitHub.

## Repos Analyzed

| # | Repo | Stars | Stack | Approach |
|---|---|---|---|---|
| 1 | [Alos21750/JableTV-MissAV-Downloader-GUI-2026](https://github.com/Alos21750/JableTV-MissAV-Downloader-GUI-2026) | 215 | Python, CustomTkinter, ffmpeg, curl_cffi | Full GUI + Docker/NAS headless |
| 2 | [AlfredoUen/JableTV](https://github.com/AlfredoUen/JableTV) | 111 | Python, Tkinter, ffmpeg | GUI tool (fork of hcjohn463/JableDownload) |
| 3 | [wmrussell8653/yt-dlp-plugin-yellow](https://github.com/wmrussell8653/yt-dlp-plugin-yellow) | 41 | Python, yt-dlp plugin | Extractor plugin for yt-dlp |

---

## Key Findings

### 1. Output Directory Handling

**All 3 repos use user-configurable save paths.** None hardcode the destination.

| Repo | Method |
|---|---|
| Alos21750 | Settings page with folder picker; saves to user-chosen directory |
| AlfredoUen | GUI config field for save location; defaults to `./` |
| yt-dlp-plugin | Leverages yt-dlp's built-in `-o` output template system |

**Our project:** Currently changed to `downloaded/` relative to CWD. Future: consider adding a settings page with configurable path.

### 2. Download Architecture

All repos converge on the same pipeline:

```
scrape HTML → extract m3u8 URL → resolve variant playlist → 
parallel segment download (2-10 threads) → AES decrypt if needed → 
concat TS → ffmpeg remux to MP4
```

**Concurrency patterns:**
- Alos21750: Configurable 2-10 parallel downloads, ThreadPoolExecutor, token-bucket rate limiter
- AlfredoUen: Single-queue sequential, but batch-add URLs
- **Our project:** 8 threads (hardcoded), ThreadPoolExecutor — matches Alos21750's pattern

### 3. Resume / Breakpoint Continuation

| Repo | Strategy |
|---|---|
| Alos21750 | `.parts/` directory with segment caching; canceled downloads can resume |
| AlfredoUen | Can continue from canceled items in the queue |
| **Our project** | `.{code}_parts/` directory — same pattern as Alos21750 |

### 4. Cloudflare / Anti-Bot Handling

**Critical finding:** jable.tv CDN may deploy Cloudflare protection. Alos21750 explicitly handles this:

- Uses `curl_cffi` (Chrome TLS fingerprint impersonation) for m3u8/key/segment requests
- Falls back to Streamtape for SupJav when Cloudflare blocks fragments
- Shows clear error message suggesting VPN/WARP when blocked
- **Our project:** `scraper.py:124-139` integrates `curl_cffi` with Chrome TLS impersonation (`impersonate="chrome120"`), falling back to `httpx` if not installed. Covered.

### 5. Multi-Site Architecture

| Repo | Sites Supported |
|---|---|
| Alos21750 | JableTV, MissAV, SupJav + generic M3U8 |
| AlfredoUen | JableTV + 14 other sites (thisav, pigav, 85tube, hanime, etc.) |
| yt-dlp-plugin | missav.com, jable.tv, 91porn.com |
| **Our project** | JableTV only (by design — v1 non-goal) |

Alos21750 uses an `M3U8Sites/` directory with site-specific extractor modules — a plugin architecture. This is the cleanest pattern for adding sites later.

### 6. File Naming

| Repo | Naming Pattern |
|---|---|
| Alos21750 | `{code} - {title}.mp4` (sanitized) |
| AlfredoUen | Webpage title as filename |
| **Our project** | `{code} - {title}.mp4` via `VideoInfo.output_filename` |

### 7. Docker / Headless Support

Alos21750 provides Docker image (`ghcr.io/alos21750/jabletv`) with:
- Multi-arch (amd64 + arm64) for NAS (Synology, QNAP)
- Headless mode via `docker_cli.py`
- `docker-compose.yml` for easy setup
- GitHub Actions CI/CD auto-builds on push

### 8. Additional Features Worth Noting

- **Clipboard monitoring** (AlfredoUen): auto-detects jable.tv URLs from clipboard and adds to queue
- **Batch import** (Alos21750): import URLs from `.txt` or `.csv` files
- **Smart clipboard** (Alos21750): background clipboard watcher
- **Automatic updater** (Alos21750): checks for new versions on startup, one-click update
- **Multi-language i18n** (Alos21750): zh-TW, zh-CN, en, jp with dark/light themes
- **Crash logging** (Alos21750): `crash_log.txt` + native crash recording
- **Built-in ffmpeg** (Alos21750): ships ffmpeg inside `.exe` — no external dependency

---

## Gaps in Our Project vs. Top Repos

| Feature | Top Repos | Our Project | Priority |
|---|---|---|---|
| Configurable output path | Yes | Environment variable (`JABLETV_DOWNLOAD_DIR`) + default `downloaded/` | Done |
| Cloudflare bypass (curl_cffi) | Yes | `scraper.py:124` uses curl_cffi with httpx fallback | Done |
| Batch URL import | Yes | No | Medium |
| Rate limiting | Yes | No | Low |
| Docker support | Yes (Alos21750) | No | Low |
| Multi-site support | Yes | No (by design) | Future |
| Download queue management | Yes | No | Medium |
| Settings page | Yes | No | Medium |
