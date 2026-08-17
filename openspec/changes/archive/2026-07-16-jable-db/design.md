## Context

Currently, when a video finishes downloading, the app shows a `DownloadCompleteScreen` with metrics, but no metadata is persisted. The `VideoInfo` dataclass (in `jabletv/scraper.py`) already holds all relevant fields (tags, actresses, category, release date, views, etc.), but it's ephemeral.

The output directory defaults to `downloaded/` (overridable via `JABLETV_DOWNLOAD_DIR` env var). Each video is saved as `<code> - <actresses>.mp4` inside that directory.

## Goals / Non-Goals

**Goals:**
- Persist `VideoInfo` as JSON after every successful download
- Store JSON files in a `jable_db/` directory alongside the video output
- Provide a TUI library screen that lists downloaded videos and supports searching by tag, actress, category, or code
- Keep the save/load layer stateless (pure functions reading/writing JSON files)

**Non-Goals:**
- No database or indexing engine — flat JSON files only
- No scraping of previously-downloaded videos (what you have is what you got)
- No deletion management (YAGNI; user can delete files manually)
- No import of videos downloaded outside the app

## Decisions

1. **Flat JSON files (one per video) over a single aggregate JSON file** — atomic per-video writes avoid corruption on crash and simplify partial updates. Each file is `<video_code>.json` in `jable_db/`.
2. **`jable_db/` lives inside the download output directory** — keeps all download artifacts together. If the user changes `JABLETV_DOWNLOAD_DIR`, the db moves with it.
3. **Save on download completion** — the save call is a side effect in `app.py:_on_complete()`, not in `downloader.py`. The downloader stays pure: receive `VideoInfo`, produce `Path`.
4. **Library screen as a separate Textual Screen** — follows the existing pattern of `LandingScreen` and `DownloadCompleteScreen`. Keeps the main app focused.
5. **Search as client-side filter on a list of all entries** — for the expected scale (tens to low hundreds of videos), loading all JSON files into memory and filtering is fast and simple. No need for incremental loading.
6. **Re-use `VideoInfo` dataclass as the data model** — no new model class. The JSON schema mirrors `VideoInfo` fields exactly. Serialization/deserialization via dataclass `asdict()` and `**kwargs`.

## Risks / Trade-offs

- **[Scale risk]** Loading hundreds of JSON files on every library open could be slow on spinning disks. → Mitigation: batch-read all files in a thread worker; cache the parsed list in memory for the session.
- **[Stale data risk]** Moving/renaming `downloaded/` or `jable_db/` externally breaks the library. → Mitigation: document that `jable_db/` is managed by the app. Accept that manual moves cause breakage.
- **[Schema drift risk]** If `VideoInfo` fields change in a future update, old JSON files won't match. → Mitigation: version the JSON with a `_version` field; deserialize with a tolerant reader that ignores unknown keys.
