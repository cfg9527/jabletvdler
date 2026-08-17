## Why

After downloading videos, there is no persistent record of what was downloaded — tags, actresses, category, release date, etc. are all lost once the download completes. A local metadata store (`jable_db/`) lets users browse/search their library by these attributes without re-scraping.

## What Changes

- Add a `jable_db/` directory in the download output directory (alongside downloaded video files)
- After each successful download, save a JSON file containing the full `VideoInfo` metadata to `jable_db/<video_code>.json`
- Add a "library" view in the TUI to browse/search previously downloaded videos by tag, actress, category, or code
- No changes to the scraping or download pipeline logic — metadata is saved as a side effect after completion

## Capabilities

### New Capabilities
- `video-metadata-store`: Persist `VideoInfo` to JSON after download; read JSON for library display; handle updates/re-downloads gracefully
- `library-browser`: TUI screen that reads `jable_db/` entries, filters by tag/actress/category/code, and shows details

### Modified Capabilities
- *(none — no existing specs are changing)*

## Impact

- **jabletv/app.py**: Wire metadata save into the download-complete flow
- **jabletv/downloader.py**: No changes (metadata save is a caller responsibility)
- **New file**: `jabletv/library.py` — library browser screen and db read/write helpers
- **New file**: `jabletv/metadata_store.py` — `save_metadata()` / `load_metadata()` / `search_metadata()` functions
- **Dependency**: No new external dependencies (stdlib `json`, `pathlib` only)
