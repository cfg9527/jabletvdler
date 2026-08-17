## Why

Currently when a download finishes, the app simply logs a green message in the RichLog and updates the status label to "Complete!" — a purely functional, emotionless notification. This is a missed opportunity to delight the user and provide a clear, actionable completion state. A dedicated "Download Complete" screen with celebratory visuals, meaningful download metrics, and clear next-action buttons transforms the end of a download from an anti-climax into a rewarding, memorable moment.

## What Changes

- **New download complete screen** — When a download finishes, instead of just logging a message, push a full-screen completion overlay that celebrates the achievement
- **4 random variant pages** — Each completion randomly shows one of 4 distinct visual concepts:
  1. **Celebratory** — "Woohoo! It's all yours!" with confetti-like ASCII art burst and festive tone
  2. **Cozy** — "Ready for your me-time." with warm, minimal, relaxing aesthetic
  3. **Sensory** — "Success! Your treasure has arrived." with sleek checkmark animation
  4. **Gamified** — "Mission Accomplished!" with pixel-art style mascot character and humorous copy
- **Download summary info** — Display video code, title, file path, file size (MB), download duration, average speed
- **Action buttons** — "Download Another" (back to main screen), "Open File/Folder" (open output directory), "Quit"
- **Track download metrics** — Record start time, end time, total bytes to compute duration and speed for display
- **TMP_jable_bye (temporary goodbye)** — A special variant that shows a farewell/bye message when the user chooses to quit after a completed download

## Capabilities

### New Capabilities
- `download-complete-screen`: Full download completion screen with 4 random visual variants (celebratory, cozy, sensory, gamified), download summary metrics, and action buttons (Download Another, Open Folder, Quit)

### Modified Capabilities
*(No existing specs to modify — this is a new capability)*

## Impact

- **`jabletv/app.py`**: Modify `_on_complete()` to push the download complete screen instead of just logging. Track download start time in `run_download()`. Pass `VideoInfo` and metrics (duration, speed, file size) to the completion screen.
- **`jabletv/downloader.py`**: Return download metrics (total bytes, elapsed time) alongside the output path so the caller can display them.
- **`jabletv/download_complete.py`** (new file): The `DownloadCompleteScreen` Screen subclass with all 4 variant layouts, copy, and ASCII art. Random variant selection logic.
- **`jabletv/themes.py`**: Add CSS for the download complete screen (variant-specific colors, completion banner styling, metrics display, action buttons).
- **New dependencies**: `pyfiglet` (already added) for variant-specific ASCII art banners.
