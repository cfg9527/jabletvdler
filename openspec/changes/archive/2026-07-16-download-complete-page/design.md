## Context

Currently, when `downloader.py` finishes downloading a video, `app.py`'s `_on_complete()` method logs a green message to the RichLog widget and sets the status label to "Complete!". There is no dedicated completion screen — the user stays on the same input form with no clear next step.

This change introduces a full-screen "Download Complete" experience that:
1. Replaces the passive log message with an immersive celebration screen
2. Shows download metrics (file size, duration, speed)
3. Provides clear next-action buttons
4. Uses 4 random visual variants to keep the experience fresh

## Goals / Non-Goals

**Goals:**
- Show a dedicated full-screen completion page when a download finishes
- Display download summary: video code, title, file path, file size, download duration, average speed
- Provide 3 action buttons: "Download Another" (pop back), "Open Folder" (open output dir), "Quit" (exit app)
- Implement 4 random variant pages with distinct visual styles and copy
- Track download start time and compute duration/speed metrics
- Use the existing pinky theme as the base, with variant-specific accent colors
- Celebrate the completion with a pyfiglet-generated banner on each variant

**Non-Goals:**
- No changes to the download pipeline itself (scraper, m3u8 parsing, segment downloading)
- No sound effects or audio cues (terminal limitation)
- No persistent completion history or log of past downloads
- No sharing or social features
- No user preference for variant selection (always random)

## Decisions

### Decision 1: Screen stacking vs. replacing content
- **Choice**: Push `DownloadCompleteScreen` on top of the main download screen via `self.push_screen()`
- **Rationale**: Consistent with the age gate pattern. The user can pop back to the main screen via "Download Another".
- **Alternative considered**: Replace widgets in the main container — mixes concerns and makes state reset harder.

### Decision 2: Random variant selection
- **Choice**: Use `random.choice()` at screen creation time from a list of 4 variant generator functions
- **Rationale**: Simple, stateless, no persistence needed. Each call to `DownloadCompleteScreen()` picks a random variant.
- **Alternative considered**: Round-robin, user preference, day-of-week based — over-engineering for a cosmetic feature.

### Decision 3: Track download metrics
- **Choice**: Record `start_time` in `run_download()`, pass `elapsed` and `total_bytes` back from `download()` return value. Compute speed as `total_bytes / elapsed`.
- **Rationale**: Minimal changes to the download pipeline. No need for a separate metrics tracking system.
- **Alternative considered**: Parse file size from filesystem after download — less accurate. Use `os.path.getsize()` as fallback.

### Decision 4: 4 variant designs (mapped to TUI capabilities)
- **Choice**: Each variant is a method on `DownloadCompleteScreen` that returns variant-specific widgets (banner ASCII art, headline, body copy, accent color). All variants share the same metrics display and action button layout.
- **Rationale**: DRY — shared layout structure with swappable content. Easy to add variant 5, 6, etc.
- **Variant 1 — Celebratory**: Banner "Woohoo!" in slant font, confetti ASCII border, coral accent
- **Variant 2 — Cozy**: Banner "Me Time." in shadow font, warm tones, sage accent
- **Variant 3 — Sensory**: Banner "Success!" in standard font, clean checkmark "\/" art, emerald accent
- **Variant 4 — Gamified**: Banner "Mission Accomplished!" in bubble font, pixel-art treasure/preview, amber accent

### Decision 5: "Open Folder" button behavior
- **Choice**: Use `subprocess.run(["open", output_dir])` on macOS, `subprocess.run(["xdg-open", output_dir])` on Linux, `os.startfile(output_dir)` on Windows
- **Rationale**: Cross-platform file manager opening. The `open` command is standard on macOS.
- **Alternative considered**: Just display the path and let the user navigate manually — less user-friendly.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| **4 variants increase code size** | Each variant is just a method returning strings + color constants. Total < 200 lines for all variants. |
| **Random variant may feel inconsistent** | Variants share the same layout structure — only colors, banners, and copy differ. Core UX is consistent. |
| **"Open Folder" is platform-specific** | Use `platform.system()` check with 3 branches. |
| **Download metrics display inaccurate** | Use `os.path.getsize()` as authoritative file size. Duration is wall-clock time. |
| **Confetti ASCII may render poorly** | Keep confetti simple (`.` `*` `+` `o` characters scattered around borders), avoid complex patterns. |
