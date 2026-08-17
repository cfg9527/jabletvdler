# JableTV Downloader

Download videos from **jable.tv** and **missav.ws** via a terminal TUI.

```
Paste URL → Scrape metadata → Download HLS segments → ffmpeg → MP4
```

## Quick Start

```bash
pip install -e ".[dev,scraper]"
jabletv
```

**Requires:** Python 3.9+, ffmpeg (`brew install ffmpeg` / `apt install ffmpeg`)

## Usage

1. Launch `jabletv` (or `python3 -m jabletv.app`)
2. Pass the age gate
3. Paste a URL and hit Download

### Supported URLs

```
https://jable.tv/videos/dldss-507/
https://missav.ws/dm26/abp-664-uncensored-leak
https://missav.com/dm26/abp-664-uncensored-leak
```

### Output

Videos go to `downloaded/` (override with `JABLETV_DOWNLOAD_DIR`).

```
downloaded/
├── ABP-664 - 彩美旬果.mp4
└── jable_db/
    ├── ABP-664.json
    └── ROE-505.json
```

### Keys

| Key | Action |
|-----|--------|
| `Enter` | Download URL |
| `l` | Library |
| `d` | Dashboard |
| `o` | Open in browser (library) |
| `Escape` | Back |

## How It Works

1. **Scraper** fetches the page, extracts video metadata and the m3u8 playlist URL
   - jable.tv: regex extraction from `<script>` variables
   - missav.ws: decodes a JavaScript packed (eval'd) string to get the playlist from surrit.com CDN
2. **Downloader** resolves the master playlist, downloads segments in parallel (8 threads), decrypts AES-128 if needed, concatenates TS files, and remuxes to MP4 via ffmpeg
3. **Metadata** (code, title, actresses, thumbnail) is saved as JSON in `jable_db/`

## Project

```
jabletv/
├── app.py              # TUI
├── scraper.py          # JableTV scraper
├── missav_scraper.py   # MissAV scraper (+ JS packer decoder)
├── downloader.py       # HLS download engine
├── metadata_store.py   # JSON metadata
├── library.py          # Downloaded video browser
├── dashboard.py        # Statistics
└── themes.py           # Pink theme
```

## Install Options

```bash
pip install -e "."                # base
pip install -e ".[dev]"           # + pytest
pip install -e ".[scraper]"       # + curl_cffi (Cloudflare bypass)
pip install -e ".[dev,scraper]"   # all
```

## Tests

```bash
python3 -m pytest tests/ -v
```
