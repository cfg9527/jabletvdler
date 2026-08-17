## Context

The current `JableDownloaderApp` is a single-screen Textual app with a minimal CSS theme using default Textual color variables (`$primary`, `$accent`, `$surface`, etc.). The app has no branding — it's a grey/blue default Textual look. We need to:

1. Add a landing screen that displays animated ASCII art
2. Re-theme the entire app with the JableTV "sexy pinky" palette

The app uses Textual v0.70+ which supports advanced theming, custom CSS variables, and `Screen` stacking. No external dependencies are needed beyond what's already in `pyproject.toml`.

## Goals / Non-Goals

**Goals:**
- Implement an animated ASCII art landing screen with ≥3 frames that cycle to create a GIF-like effect
- Apply the JableTV color palette across all widgets: header, footer, buttons, inputs, progress bar, log, labels
- Provide a smooth transition from landing to the main download screen on keypress
- Keep the existing download workflow untouched
- Make the theme easy to modify (centralized color constants)

**Non-Goals:**
- No changes to the scraper, downloader, or video info logic
- No new keyboard shortcuts or interactions beyond landing → main transition
- No configuration file for theme switching (theme is hardcoded for now)
- No unit tests for ASCII art rendering (visual/acceptance only)

## Decisions

### Decision 1: Screen stacking vs. widget visibility
- **Choice**: Use Textual `Screen` stack (push landing screen, then pop/dismiss to reveal main screen)
- **Rationale**: Cleaner separation — the landing screen has its own compose, mount, and event handling. Widget visibility toggling (`display: none`) would pollute the main app's compose method.
- **Alternative considered**: Using a `Container` with `display: none` toggle — rejected because it mixes concerns and makes the compose method harder to read.

### Decision 2: Frame animation mechanism
- **Choice**: `set_interval` timer on the landing screen that cycles through a list of ASCII art strings, updating a `Static` widget
- **Rationale**: Textual's built-in `set_interval` is lightweight and accurate enough for a ~200ms frame rate. No threading or async needed.
- **Alternative considered**: `@work(thread=True)` with `call_from_thread` — overkill for UI-only animation. The timer approach is simpler and keeps everything in the UI thread.

### Decision 3: Theme implementation
- **Choice**: Define a `PinkyTheme` class with Textual CSS as a class variable + color constants, applied by setting `self.CSS` on the app class
- **Rationale**: Textual supports per-app CSS via the `CSS` class variable. We can override it at runtime or use `self.dark = True` + custom CSS variables. Centralizing colors in a `themes.py` module allows future theme switching.
- **Alternative considered**: Inline CSS in `app.py` — simpler but harder to maintain. Separate CSS file — Textual can load external `.tcss` files but that adds a file dependency.

### Decision 4: ASCII art subject
- **Choice**: A stylized "JableTV" logo text in ASCII, possibly with a video play button motif, surrounded by decorative borders
- **Rationale**: The JableTV brand uses a simple text logo. ASCII art of the actual website logo is recognizable but no copyright concerns since it's text-based.
- **Alternative considered**: ASCII art of a video player or actress silhouette — too complex for ASCII and potentially problematic.

### Decision 5: Color palette mapping to Textual variables
- **Choice**: Map JableTV colors to Textual's built-in theme variables:
  - `$primary` → Periwinkle gradient start (`#91a5f4`)
  - `$accent` → Hot pink (`#fe628e`)
  - `$surface` → Dark background (`#161a26`)
  - `$text` → Light grey (`#e0e0e0`)
  - `$text-muted` → Muted grey (`#8e9194`)
  - `$error` → Coral/red (`#ff8382`)
  - `$success` → Submit green (`#1db954`)
  - Screen background → `#161a26`
  - Container borders → `#191d28`
- **Rationale**: Textual's theming system uses these variable names consistently across widgets. Overriding them at the app level automatically propagates to Header, Footer, Button, Input, etc.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| **ASCII art animation may flicker** on slow terminals | Keep frame count low (3-5 frames) and frame rate moderate (250-300ms). Test on iTerm2, Terminal.app, and tmux. |
| **Hot pink accent may be hard to read** on dark background | Ensure sufficient contrast ratio (WCAG AA). Use lighter pink `#ff6a88` for active states and white text on pink backgrounds. |
| **Textual CSS variable overrides may break** in future Textual versions | Pin Textual version in `pyproject.toml`. Wrap theme in a version check if needed. |
| **Landing screen adds startup latency** | ASCII frames are small strings (< 2KB total), loaded synchronously. No network calls. Negligible impact. |
