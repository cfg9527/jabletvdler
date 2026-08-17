## 1. Metadata Store Module

- [x] 1.1 Create `jabletv/metadata_store.py` with `save_metadata(video: VideoInfo, output_dir: str) -> Path` function
- [x] 1.2 Implement JSON serialization with `_version` field and dataclass `asdict()` output
- [x] 1.3 Implement `load_all_metadata(output_dir: str) -> list[dict]` that reads all `<code>.json` files from `jable_db/`
- [x] 1.4 Implement `search_metadata(entries: list[dict], query: str) -> list[dict]` that filters by code/tag/actress/category (case-insensitive)
- [x] 1.5 Write unit tests for metadata_store.py (save, load, search, tolerant reader)

## 2. Wire Save Into App

- [x] 2.1 In `app.py:_on_complete()`, call `save_metadata()` after successful download
- [x] 2.2 Derive `jable_db/` path from `output_dir` (same as videos)
- [ ] 2.3 Verify metadata file is written during manual download test

## 3. Library Browser Screen

- [x] 3.1 Create `jabletv/library.py` with a new Textual `Screen` subclass (`LibraryScreen`)
- [x] 3.2 Add a library list widget showing code, title, actresses, and tags for each entry
- [x] 3.3 Add a search `Input` that filters the list in real-time by code/tag/actress/category
- [x] 3.4 Add a detail panel showing full metadata when an entry is selected
- [x] 3.5 Add an "Open URL" action that opens `https://jable.tv/videos/<code>/` in default browser
- [x] 3.6 Handle empty state (no jable_db/ or empty) with a friendly message

## 4. Navigation & Integration

- [x] 4.1 Add a "Library" button to the main app UI that pushes `LibraryScreen`
- [x] 4.2 Add a keyboard shortcut for quick access to library (`l` key)
- [x] 4.3 Ensure `LibraryScreen` has a "Back" (button + escape) handler to return to main screen
- [ ] 4.4 Run app and test full flow: download → check jable_db/ → open library → search → view details
