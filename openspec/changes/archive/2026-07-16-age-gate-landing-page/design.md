## Context

The current `LandingScreen` in `jabletv/landing.py` implements an animated ASCII art showcase (JableTV logo with play button) that auto-dismisses on any key press or click. This was designed as a branded splash screen. We need to replace it with an 18+ age verification gate that:

1. Displays "JABLETV_DL" in large ASCII art (static, no animation needed)
2. Shows a dual-language (EN + JP) age warning
3. Presents two explicit buttons: "Yes, I am 18+" and "No"
4. Only proceeds to the main app on explicit "Yes" click; exits on "No"

The age gate pattern follows standard adult-content websites where users must self-certify age before accessing content.

Separately, the entire application lacks structured logging. Errors are either silently caught or only shown in the TUI's RichLog widget. A centralized logging system with file output will capture all errors for debugging and support purposes.

## Goals / Non-Goals

**Goals:**
- Replace the animated ASCII art with static "JABLETV_DL" word art in DeepPink (`#ff1493`)
- Display English and Japanese age consent warnings
- Implement Yes/No buttons with clear visual distinction
- "Yes, I am 18+" → dismiss gate and show main download screen
- "No" → immediately exit the application
- Retain the pinky theme styling (dark background, hot pink accents)
- Keep the existing button/theme CSS as much as possible
- Setup centralized logging with dual output: `log/app.log` (INFO+) and `log/error.log` (ERROR+)
- Add structured logging calls to `app.py`, `downloader.py`, `scraper.py`, and `landing.py`
- Use log rotation to prevent unbounded disk usage

**Non-Goals:**
- No changes to the download workflow or app logic
- No persistence or cookie-based age gate (always shows on startup)
- No customization of the Japanese text (hardcoded for now)
- No animation or cycling frames on the age gate
- No remote logging, Sentry, or external log aggregation
- No log level configuration via environment variables (hardcoded for now)

## Decisions

### Decision 1: Static ASCII art vs. animated
- **Choice**: Static ASCII art displaying "JABLETV_DL" in large block letters, with no frame cycling
- **Rationale**: The age gate is a serious legal notice — animation would undermine the gravity. The previous decorative animation is removed entirely.
- **Alternative considered**: Subtle pulsing effect on the ASCII text — discarded as unnecessary complexity for a compliance screen.

### Decision 2: Button behavior — "No" exits the app
- **Choice**: Pressing "No" calls `self.app.exit()` with return code 0
- **Rationale**: Standard expectation for age gates — clicking "No" means "leave this site." The app should terminate cleanly.
- **Alternative considered**: "No" navigates to a blank/blocked screen — more complex and non-standard for age gates.

### Decision 3: Button layout
- **Choice**: Center-aligned horizontal row of two buttons, "Yes" in hot pink (`#fe628e`), "No" in a muted/dark grey
- **Rationale**: Hot pink matches the accent color and draws attention to the affirmative action. Muted grey makes "No" visually de-emphasized but still accessible.
- **Alternative considered**: Stacked vertically — takes more vertical space on already content-heavy screen.

### Decision 4: ASCII art color
- **Choice**: Render the "JABLETV_DL" ASCII art in DeepPink `#ff1493` instead of the standard hot pink `#fe628e`
- **Rationale**: DeepPink `#ff1493` is a more vibrant, eye-catching pink that stands out better on the dark background, giving the age gate header more visual punch.

### Decision 5: No age gate animation timer
- **Choice**: Remove `set_interval` and `_timer_handle` entirely from `LandingScreen`
- **Rationale**: Age gate is a static screen — no animated frames needed. User must actively click a button.
- **Alternative considered**: Keep the timer as a subtle background effect on the ASCII art — adds complexity with no legal/compliance benefit.

### Decision 6: Logging module design
- **Choice**: Create `jabletv/logger.py` with a `setup_logging()` function that configures two `RotatingFileHandler` instances:
  - `log/app.log` — captures all INFO+ messages (max 5MB, 3 backup files)
  - `log/error.log` — captures only ERROR+ messages (max 5MB, 3 backup files)
  - Format: `[%(asctime)s] %(levelname)-8s %(name)s: %(message)s` with ISO 8601 timestamps
  - Root logger level set to INFO
- **Rationale**: `RotatingFileHandler` is built into Python stdlib — no external dependencies. Dual-file setup means support can check `error.log` for quick diagnosis without wading through routine INFO messages. The `log/` directory is created automatically on first log write.
- **Alternative considered**: Single log file — harder to isolate errors. Syslog — platform-dependent. Loguru — external dependency.

### Decision 7: Logger usage pattern
- **Choice**: Each module creates its own logger via `logging.getLogger(__name__)` at module level
- **Rationale**: Standard Python logging pattern. The logger name (e.g., `jabletv.downloader`) appears in log output, making it easy to trace which module generated each message.
- **Alternative considered**: Single global logger — loses module context in log output.

### Decision 8: Log directory location
- **Choice**: `log/` directory at the project root (relative to CWD when running `python -m jabletv`)
- **Rationale**: Standard convention for Python tools. The `log/` directory is gitignored (add to `.gitignore` if not already there).
- **Alternative considered**: `~/Library/Logs/jabletv/` on macOS — harder for users to find. `$HOME/.jabletv/logs/` — adds XDG complexity.

### Decision 9: All changes in `landing.py` only (age gate)
- **Choice**: Keep all age gate logic within `landing.py`. `app.py` remains unchanged in terms of screen stacking (already pushes `LandingScreen` on mount and pops on "Yes").
- **Rationale**: Clean separation of concerns. The age gate is a screen-level concern.
- **Alternative considered**: Inline age gate in `app.py` — mixes app startup logic with UI screen.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| **"No" exit feels abrupt** — no confirmation dialog | Standard for age gates. Single click to exit is intentional. |
| **Japanese text may render wrong** on some terminals | Use basic Unicode characters. The Japanese text uses common CJK characters that all modern terminals support. |
| **Buttons too close together** — risk of mis-click | Add `margin: 1` between buttons in CSS. Make buttons visually distinct with different colors. |
| **Age gate is a blocker** for returning users | This is intentional — age gate shows on every launch. No cookie/persistence mechanism. |
| **Log files grow unbounded** | `RotatingFileHandler` with max 5MB per file and 3 backups keeps total under ~20MB per log |
| **Log directory missing** | `setup_logging()` creates `log/` with `os.makedirs(exist_ok=True)` on initialization |
| **Logging adds disk I/O** | INFO-level logging is moderate — downloader/scraper logs are at DEBUG level by default to avoid excessive writes |
