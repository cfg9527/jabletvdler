## 1. Create Download Complete Module

- [x] 1.1 Create `jabletv/download_complete.py` with `DownloadCompleteScreen(Screen)` class
- [x] 1.2 Implement shared layout: metrics display area, action buttons area, variant content area
- [x] 1.3 Implement variant selection: `random.choice()` from 4 variant methods
- [x] 1.4 Add platform-specific "Open Folder" helper (`open` / `xdg-open` / `os.startfile`)

## 2. Implement Variant Designs

- [x] 2.1 **Celebratory variant**: pyfiglet "Woohoo!" (slant), confetti border, coral accent, "It's all yours!"
- [x] 2.2 **Cozy variant**: pyfiglet "Me Time." (shadow), sage accent, warm copy
- [x] 2.3 **Sensory variant**: pyfiglet "Success!" (standard), ASCII checkmark, emerald accent, sleek copy
- [x] 2.4 **Gamified variant**: pyfiglet "Mission Accomplished!" (bubble), pixel-art treasure box, amber accent, funny copy

## 3. Add Theme CSS for Completion Screen

- [x] 3.1 Add variant accent color constants to `PinkyTheme`
- [x] 3.2 Add CSS for completion screen layout (centered variant content, metrics grid, action button row)
- [x] 3.3 Style metrics display (labels in muted text, values in bright text, aligned columns)
- [x] 3.4 Style action buttons ("Download Another" in primary, "Open Folder" in secondary, "Quit" in danger)

## 4. Track Download Metrics in Pipeline

- [x] 4.1 In `app.py`, record `start_time` when `run_download()` is called
- [x] 4.2 Modify `_on_complete()` to compute elapsed time, get file size, and push `DownloadCompleteScreen`
- [x] 4.3 Pass `VideoInfo`, output path, file size (MB), duration, and speed to the completion screen via constructor

## 5. Implement TMP_jable_bye Farewell Screen

- [x] 5.1 Create farewell variant showing pyfiglet "Bye!" banner + goodbye message
- [x] 5.2 On "Quit" click, push farewell screen with `set_timer(2, self.app.exit)` for auto-dismiss

## 6. Cleanup & Verification

- [ ] 6.1 Run `ruff check jabletv/` and fix any lint issues
- [ ] 6.2 Run `mypy jabletv/` and fix any type issues
- [ ] 6.3 Run `python -m jabletv` and complete a download to verify the completion screen appears
- [ ] 6.4 Verify all 4 variants display correctly (run multiple downloads)
- [ ] 6.5 Verify "Download Another" returns to main screen with a clean state
- [ ] 6.6 Verify "Open Folder" opens the file manager
- [ ] 6.7 Verify "Quit" shows the farewell screen then exits
- [ ] 6.8 Verify metrics (file size, duration, speed) display accurately
