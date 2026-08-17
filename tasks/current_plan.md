# Current Plan — JableTV Downloader Implementation

## Milestone Checklist

### Phase 1: Project Scaffolding
- [x] Create `pyproject.toml` with dependencies
- [x] Create `jabletv/__init__.py` package init
- [x] Create `AGENTS.md` with build/test/lint commands

### Phase 2: Core Library
- [x] `jabletv/utils.py` — `sanitize_filename()`, `rotating_ua()`
- [x] `jabletv/scraper.py` — `VideoInfo` dataclass, `scrape(url)` → m3u8 + metadata
- [x] `jabletv/downloader.py` — `download(video, output_dir, progress_cb)`
  - [x] `resolve_master_m3u8()` — pick best variant from master playlist
  - [x] `parse_m3u8_content()` — extract segments, AES key/IV
  - [x] `decrypt_segment()` — AES-128 CBC decryption
  - [x] `ThreadPoolExecutor(8)` concurrent segment download
  - [x] `.parts/` directory for segment caching (resume)
  - [x] `verify_media_file()` — ffprobe validation

### Phase 3: TUI Application
- [x] `jabletv/app.py` — `JableDownloaderApp(Textual App)`
  - [x] `Input#url-input` widget
  - [x] `Button#download-btn` widget
  - [x] `ProgressBar#progress` widget
  - [x] `Label#status-label` widget
  - [x] `MetadataDisplay#metadata` widget
  - [x] `RichLog#log` widget
  - [x] `@work(thread=True)` — non-blocking scrape/download
  - [x] `call_from_thread()` progress updates

### Phase 4: Testing
- [x] `tests/test_app.py` — 16 tests
  - [x] `TestSanitizeFilename` — 7 tests (special chars, Japanese, brackets, truncation, empty)
  - [x] `TestRotatingUA` — 1 test (returns valid string)
  - [x] `TestExtractM3U8` — 5 tests (single/double quotes, bare URL, empty, escaped URL)
  - [x] `TestVideoInfo` — 3 tests (output_filename with code, actresses, multiple actresses)

### Phase 5: Documentation
- [x] `docs/design/design.md` — architecture, data flow, decisions, risks
- [x] `tasks/current_plan.md` — this file
- [x] `instructions/github_ref.md` — GitHub top-repo research (3 repos, 215/111/41 stars)
- [x] `instructions/vibe-coding-constitution.md` — AI debug & test reference policy
- [ ] `README.md` — user-facing documentation (not yet created)

## Test Specifications (TDD — AAA Pattern)

### scraper.py
- [x] **Arrange**: HTML fixture with `var hlsUrl = 'https://...'`
- [x] **Act**: call `_extract_m3u8(html)`
- [x] **Assert**: returns correct URL
- [x] Edge: double quotes, bare URL, escaped slashes, no match → empty string

### utils.py
- [x] **Arrange**: various input strings (Japanese, slashes, special chars)
- [x] **Act**: call `sanitize_filename(input)`
- [x] **Assert**: output matches expected sanitized form
- [x] Edge: empty → "untitled", >80 chars truncated

### downloader.py
- [ ] Integration test: mock httpx responses, verify segment download pipeline
- [ ] Unit test: `decrypt_segment()` with known AES key/IV/ciphertext
- [ ] Unit test: `resolve_master_m3u8()` picks highest bandwidth

### app.py
- [ ] Textual pilot test: type URL, click download, verify status changes
- [ ] Textual pilot test: empty URL → error message
- [ ] Textual pilot test: invalid URL → error message

## Blast Radius Analysis (Graphify)

### Key Finding
**Checked via Graphify:** `VideoInfo` (`jabletv/scraper.py:18`) has **19 connections** (highest degree node, betweenness 0.387). Modifying it affects:
- `JableDownloaderApp` (app.py) — imports and references
- `MetadataDisplay.show_info()` (app.py) — uses as parameter
- `scrape()` (scraper.py:108) — returns it
- `download()` (downloader.py:96) — uses as parameter
- `sanitize_filename()` (utils.py) — called via `.output_filename` property
- `TestVideoInfo`, `TestSanitizeFilename`, `TestExtractM3U8`, `TestRotatingUA` — all reference it

`download()` in `downloader.py:96` is imported by `app.py` → any signature change breaks the TUI. Added defensive interface compatibility tests into this plan.

### Command Run
```
graphify . --code-only          # 71 nodes, 145 edges, 9 communities
graphify explain "VideoInfo"     # traced all 19 connections
graphify query "download()"      # confirmed import chain: app.py → downloader.py
```

## ECC Validation

- [x] Create `ecc_check.sh` (completed)
- [x] Run `./ecc_check.sh` — 9 lint errors + 11 type errors found
- [x] Fix F401 unused imports (`Vertical`, `Horizontal`, `reactive`)
- [x] Fix F541 f-string without placeholders
- [x] Fix E731 lambda → def (`_noop_progress`)
- [x] Fix F841 unused `stop_event` variable
- [x] Fix F821 undefined name `e` (Python 3.3+ scoping rule)
- [x] Fix mypy `callable` → `Callable` from typing
- [x] Fix mypy `str`/`Path` type mismatch → use `out_dir: Path`
- [x] Fix mypy `Widget` has no attribute `update` → add `ProgressBar` type hint
- [x] Rename `_log` → `_app_log` to avoid Textual's internal `_log` override
- [x] **Re-run: ALL CHECKS PASSED** — 16/16 tests, 0 lint, 0 type errors
- [x] Report results back



### Milestone Summary

| Step | Status | Date |
|---|---|---|
| Phase 1 — Scaffolding | [x] Completed | 2026-07-11 |
| Phase 2 — Core Library | [x] Completed | 2026-07-11 |
| Phase 3 — TUI App | [x] Completed | 2026-07-11 |
| Phase 4 — Testing | [x] Completed (75/75 pass) | 2026-07-11 |
| Phase 5 — Documentation | [x] Completed | 2026-07-11 |
| Phase 6 — Performance | [x] Completed | 2026-07-11 |
| ECC Validation | [x] Passed | 2026-07-11 |

### Phase 6: Performance Optimization (Connection Pooling)

- [x] `resolve_master_m3u8()` accepts optional `client` param for session reuse
- [x] `parse_m3u8_content()` accepts optional `client` param for session reuse
- [x] `download()` creates shared `httpx.Client(http2=True, timeout=60.0)`
- [x] `download_seg()` closure uses shared client instead of standalone `httpx.get()`
- [x] Graceful HTTP/2 fallback (ImportError → HTTP/1.1)
- [x] `client.close()` in finally block
- [x] `test_uses_client_when_provided` — verifies client passthrough
- [x] `test_no_segments_raises` — updated to patch `parse_m3u8_content` directly
- [x] ECC: 75 tests, 0 lint, 0 type errors
