## 1. Pinky Theme Module

- [x] 1.1 Create `jabletv/themes.py` with `PinkyTheme` class containing color constants and CSS string
- [x] 1.2 Define all color constants (primary gradient, accent hot pink, surface darks, text colors, success green)
- [x] 1.3 Write the Textual CSS string with theme variable overrides (`$primary`, `$accent`, `$surface`, etc.)
- [x] 1.4 Add widget-specific CSS for Header, Button, Input, ProgressBar, Footer, Container borders using pinky palette
- [x] 1.5 Verify theme class exports cleanly with `from jabletv.themes import PinkyTheme`

## 2. ASCII Art Landing Screen

- [x] 2.1 Create `jabletv/landing.py` with `LandingScreen(Textual Screen subclass)` class
- [x] 2.2 Design 3-5 ASCII art frames featuring a stylized "JableTV" logo with play-button motif
- [x] 2.3 Implement `compose()` with a Static widget for ASCII art, a Label for tagline, and a Label for "Press any key" prompt
- [x] 2.4 Implement `on_mount()` with `set_interval` (250-300ms) to cycle through ASCII art frames
- [x] 2.5 Implement key press and mouse click handlers (`on_key`, `on_click`) to dismiss the screen
- [x] 2.6 On dismissal, pop the landing screen and reveal the main download screen

## 3. Apply Theme to Main App

- [x] 3.1 In `jabletv/app.py`, import `PinkyTheme` from `jabletv.themes`
- [x] 3.2 Set `CSS = PinkyTheme.CSS` on `JableDownloaderApp` class (or compose at runtime)
- [x] 3.3 Remove or replace the old inline CSS in `app.py`
- [x] 3.4 Verify all theme variables propagate to Header, Footer, Button, Input, ProgressBar, and containers

## 4. Wire Landing Screen into App Startup

- [x] 4.1 In `app.py`, update `on_mount()` or compose to push `LandingScreen` as an initial screen
- [x] 4.2 Ensure the landing screen is the first thing shown before the main download interface
- [x] 4.3 Verify that after dismissal, the main download screen appears with full functionality

## 5. Cleanup & Verification

- [x] 5.1 Remove any temporary flat spec files from the change directory
- [ ] 5.2 User to run `python -m jabletv` and verify: landing screen displays with animated ASCII art
- [ ] 5.3 User to verify: pressing any key dismisses landing screen and shows themed main UI
- [ ] 5.4 User to verify: download workflow (paste URL → scrape → download → progress → complete) works end-to-end
- [ ] 5.5 User to verify: all UI elements use pinky theme colors (hot pink accents, dark backgrounds, periwinkle-purple gradient)
- [x] 5.6 Run `ruff check jabletv/` and fix any lint issues
- [x] 5.7 Run `mypy jabletv/` and fix any type issues
