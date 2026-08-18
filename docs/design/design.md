# JableTV Downloader — Design Document

Visual taste primer (palette, chrome, motion, screens): [taste.html](./taste.html)

## Context
A terminal-based video downloader for jable.tv that uses HLS (m3u8) streaming protocol.
Target audience: technical users comfortable with the terminal.

## Goals
- Download videos from jable.tv via URL input
- Provide a Textual TUI with real-time progress feedback
- Support concurrent segment downloading for speed
- Handle AES-128 encrypted HLS streams
- Produce clean MP4 output via ffmpeg

## Non-Goals
- No web UI or browser-based interface
- No multi-site support (MissAV, SupJav) in v1
- No crawling/search functionality — single URL download only
- No Docker packaging in v1

## Architecture

### Component Tree
```
JableDownloaderApp (Textual App)
├── Header
├── Container#main-container
│   ├── Input#url-input          → user pastes URL
│   ├── Button#download-btn       → triggers download
│   ├── ProgressBar#progress      → segment progress 0-100
│   ├── Label#status-label        → status text update
│   ├── MetadataDisplay#metadata  → scraped video info
│   └── RichLog#log              → event log
└── Footer
```

### Data Flow
```
User URL → scraper.scrape(url) → VideoInfo(dataclass)
                                    │
                                    ▼
         downloader.download(video, progress_cb)
           ├── resolve_master_m3u8()    → variant playlist URL
           ├── parse_m3u8_content()     → segments[], key, iv
           ├── ThreadPoolExecutor(8)    → concurrent segment download
           │     ├── AES-CBC decrypt (if encrypted)
           │     └── .parts/ cache for resume
           ├── concat .ts segments
           └── ffmpeg → output.mp4
```

### Dependencies
- `textual` — TUI framework
- `httpx` — async-first HTTP client (h2 support)
- `m3u8` — HLS playlist parser
- `cryptography` — AES-128 CBC decryption
- `ffmpeg` — system binary for TS→MP4 conversion

## Decisions
1. **Textual over CustomTkinter**: Terminal-native, works over SSH, Rich integration
2. **httpx over requests**: h2 support needed for CDN connection pools
3. **ThreadPoolExecutor over asyncio**: Segment downloads are I/O-bound, threads simpler
4. **ffmpeg merge over manual concat**: Needed for proper MP4 container with faststart

## Risks / Tradeoffs
- jable.tv may change their m3u8 embedding pattern → regex extraction needs monitoring
- CDN may add Cloudflare protection → may need curl_cffi migration
- ffmpeg must be installed on the user's system → documented requirement
- Python 3.9 compatibility limits type annotation syntax
