## 1. Replace ASCII Art & Remove Animation

- [x] 1.1 Replace the `FRAMES` list in `landing.py` with a single static ASCII art string of "JABLETV_DL" in large block letters
- [x] 1.2 Remove `set_interval`, `_timer_handle`, `_next_frame`, `_update_frame`, and all timer-related code from `LandingScreen`
- [x] 1.3 Remove the `Timer` import from `textual.timer` (no longer needed)
- [x] 1.4 Update `on_mount()` to just display the static ASCII art once (no frame cycling)

## 2. Add Age Warning Text

- [x] 2.1 Add English warning text constant: "WARNING: This site contains adult content. You must be at least 18 years old to enter. By entering, you confirm that you are of legal age."
- [x] 2.2 Add Japanese warning text constant: "警告：このサイトには成人向けコンテンツが含まれています。入場するには18歳以上である必要があります。入場することにより、あなたが法的な成人年齢（18歳以上）であることを確認したことになります。"
- [x] 2.3 Add `Label` widgets for both warning texts in `compose()` below the ASCII art
- [x] 2.4 Style warning text with appropriate colors (yellow/amber for warnings, white text)

## 3. Add Yes/No Buttons

- [x] 3.1 Add `Button` widget for "Yes, I am 18+" with hot pink (`#fe628e`) styling
- [x] 3.2 Add `Button` widget for "No" with muted grey styling
- [x] 3.3 Wire "Yes" button (`on_button_pressed`) to `self.app.pop_screen()` to reveal main download UI
- [x] 3.4 Wire "No" button to `self.app.exit()` to quit the application
- [x] 3.5 Remove `on_key` and `on_click` handlers (age gate requires explicit button interaction)

## 4. Update Theme CSS for Age Gate

- [x] 4.1 Add age gate-specific CSS to `themes.py` (age-gate container, warning text colors, button styles)
- [x] 4.2 Style "Yes" button with hot pink accent, white text, bold
- [x] 4.3 Style "No" button with muted/dark grey background, subtle text
- [x] 4.4 Ensure the "JABLETV_DL" ASCII art uses DeepPink (`#ff1493`) color

## 5. Create Logging Module

- [x] 5.1 Create `jabletv/logger.py` with `setup_logging()` function using `RotatingFileHandler`
- [x] 5.2 Configure dual handlers: `log/app.log` (INFO+) and `log/error.log` (ERROR+) with 5MB / 3-backup rotation
- [x] 5.3 Add `get_logger(name)` factory that calls `logging.getLogger(name)`
- [x] 5.4 Add `os.makedirs("log", exist_ok=True)` in setup to auto-create log directory
- [x] 5.5 Add `log/.gitkeep` to track the empty directory in git

## 6. Integrate Logging Across Modules

- [x] 6.1 In `app.py`: add `setup_logging()` call at startup, log app start/shutdown, log errors
- [x] 6.2 In `downloader.py`: add module-level logger, log download start/complete/errors at appropriate levels
- [x] 6.3 In `scraper.py`: add module-level logger, log scrape attempts and failures
- [x] 6.4 In `landing.py`: add module-level logger, log age gate display and user choice (Yes/No)

## 7. Cleanup & Verification

- [x] 7.1 Run `ruff check jabletv/` and fix any lint issues
- [x] 7.2 Run `mypy jabletv/` and fix any type issues
- [ ] 7.3 Run `python -m jabletv` and verify: age gate shows with "JABLETV_DL" ASCII art in DeepPink (`#ff1493`)
- [ ] 7.4 Verify: English and Japanese warning text is displayed
- [ ] 7.5 Verify: clicking "Yes, I am 18+" proceeds to themed download UI
- [ ] 7.6 Verify: clicking "No" exits the application
- [ ] 7.7 Verify: pressing any key does NOT dismiss the gate (must use buttons)
- [ ] 7.8 Verify: `log/app.log` and `log/error.log` are created after running the app
- [ ] 7.9 Verify: error log contains ERROR level messages (trigger a download error to test)
