## Why

The current landing screen shows a decorative "JableTV" ASCII logo with a play button and a simple "Press any key" prompt. While visually branded, it lacks an age-gate mechanism which is a legal and ethical requirement for adult content tools. Adding an 18+ age verification screen with explicit warnings in English and Japanese, plus explicit "Yes/No" buttons, makes the application compliant with responsible adult-content distribution practices and matches the industry-standard 18+ web gate pattern.

Additionally, the application has zero structured logging — errors are silently swallowed or only shown in the TUI. Adding file-based logging with a dedicated `log/` directory ensures errors are captureable for debugging and user support.

## What Changes

- **Replace ASCII art** — Change the animated frames from the "JableTV Downloader" logo to the word "JABLETV_DL" in large block ASCII art rendered in DeepPink (`#ff1493`)
- **Add 18+ age verification warning** — Display dual-language (English + Japanese) age consent text below the ASCII art
- **Add "Yes (18+)" and "No" buttons** — Instead of "press any key", show two interactive buttons
- **Remove auto-advance animation** — The age gate is a static screen with clickable buttons, no cycling ASCII frames needed
- **Setup application logging** — Configure Python's `logging` module to write logs to a `log/` directory, with error-level and above also logged to a separate `log/error.log` file
- **Integrate logging across modules** — Replace ad-hoc error handling in `app.py`, `downloader.py`, `scraper.py` with structured logging calls

## Capabilities

### New Capabilities
- `age-gate-screen`: Full 18+ age verification gate with dual-language warning, "JABLETV_DL" ASCII art header, and Yes/No buttons that control app flow (enter vs. exit)
- `error-logging`: Application-wide structured logging setup using Python's `logging` module, with INFO-level logs written to `log/app.log` and ERROR-level+ logs written to `log/error.log`, with log rotation

### Modified Capabilities
- `ascii-landing-page`: The existing landing screen is being **replaced** by the age gate. Requirements change from animated decorative landing to static age verification gate with buttons.

## Impact

- **`jabletv/landing.py`**: Complete rewrite of the `LandingScreen` class — replace `FRAMES` with static "JABLETV_DL" ASCII art, remove timer/animation, add text labels for warnings, add Button widgets for Yes/No, wire button actions to `pop_screen` (Yes) or `exit` (No)
- **`jabletv/app.py`**: Add logging calls for app start/stop, error states. Import and initialize the logging module.
- **`jabletv/themes.py`**: May need button-specific CSS for the age gate buttons
- **`jabletv/logger.py`** (new file): Centralized logging configuration with dual handlers (app.log + error.log), log rotation, and a `get_logger()` factory function
- **`jabletv/downloader.py`**: Add logging calls for download progress, errors, segment failures
- **`jabletv/scraper.py`**: Add logging calls for scrape attempts, failures, retries
- **`log/.gitkeep`** (new): Empty directory placeholder for the log folder
- **No new dependencies** — uses only Python standard library `logging` + `logging.handlers.RotatingFileHandler`
