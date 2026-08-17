## Why

The current TUI app launches directly into a functional URL-input/download interface with no visual identity — it's utilitarian but lacks personality. The JableTV brand has a distinct visual aesthetic ("sexy pinky": hot pink accents, periwinkle-to-purple gradients, dark backgrounds) that the desktop app should echo. Adding an animated ASCII art landing page and re-theming the UI to match the JableTV color scheme will create a cohesive, branded experience that makes the tool feel polished and intentional.

## What Changes

- **Landing page with animated ASCII art** — When the app starts, instead of jumping straight into the download UI, show a full-screen landing screen featuring animated ASCII art (the JableTV logo/video motif rendered in ASCII, with a frame animation loop creating a "GIF-like" effect), plus a tagline "JableTV Downloader" and a prompt to press any key to continue.
- **"Sexy pinky" UI theme** — Re-color the entire Textual TUI to match the JableTV website palette:
  - Primary gradient: periwinkle blue → soft purple (`#91a5f4` → `#b08cf9`)
  - Accent hot pink: `#fe628e` for interactive highlights, hover states, focus rings
  - Secondary pink: `#ff6a88` for active/favorite states
  - Dark backgrounds: `#161a26` and `#191d28` for screens and containers
  - Coral: `#ff8382` for secondary accents
  - Muted text: `#8e9194`, `#b8babc`
- **Landing → main UI transition** — Press any key or click to dismiss the landing page and reveal the existing download workflow, now fully re-themed.
- **No functional changes** — The download (scrape, progress, completion) workflow remains identical; only the presentation layer changes.

## Capabilities

### New Capabilities
- `ascii-landing-page`: Animated ASCII art landing screen shown on app startup, with frame-based animation and a key-press-to-dismiss transition into the main UI.
- `pinky-theme`: The complete Textual theme (CSS variables, color overrides, widget styling) that implements the JableTV "sexy pinky" color palette across all screens and widgets.

### Modified Capabilities
*(No existing specs to modify — this is the first capability set for this project.)*

## Impact

- **`jabletv/app.py`**: Major changes to the `JableDownloaderApp` class — add landing screen compose/mount logic, theme override, and transition handling.
- **`jabletv/themes.py`** (new file): Central theme definition with Textual CSS and color constants for the pinky palette.
- **`jabletv/landing.py`** (new file): ASCII art frames, animation logic, and landing screen widget.
- **`pyproject.toml`**: No new dependencies required — animated ASCII art uses only Textual's built-in `Static` widget with timer-driven frame switching.
