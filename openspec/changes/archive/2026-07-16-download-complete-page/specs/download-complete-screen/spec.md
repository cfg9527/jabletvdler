## ADDED Requirements

### Requirement: Download complete screen display
The system SHALL display a full-screen download completion page when a download finishes successfully, replacing the current log-only notification.

#### Scenario: Completion screen appears
- **WHEN** a download reaches 100% and completes successfully
- **THEN** the system SHALL push a full-screen completion overlay
- **AND** the main download screen SHALL remain underneath (accessible via "Download Another" button)
- **AND** the RichLog SHALL still contain the completion message as a fallback

### Requirement: Download summary metrics
The system SHALL display download summary information on the completion screen.

#### Scenario: Metrics displayed
- **WHEN** the completion screen is shown
- **THEN** it SHALL display the following metrics:
  - Video code (e.g., "JUR-603")
  - Video title
  - Output file path
  - File size in MB (with 1 decimal precision)
  - Download duration in minutes:seconds format
  - Average download speed in MB/s

### Requirement: Random variant selection
The system SHALL randomly select one of 4 visual variants each time a download completes.

#### Scenario: Random variant shown
- **WHEN** the completion screen is created
- **THEN** one of the 4 variants SHALL be selected uniformly at random
- **AND** the same variant SHALL NOT be guaranteed on consecutive downloads
- **AND** each variant SHALL have distinct banner ASCII art, headline copy, body copy, and accent color

### Requirement: Variant 1 — Celebratory
The "Celebratory" variant SHALL use festive, high-energy visuals.

#### Scenario: Celebratory variant renders
- **WHEN** the celebratory variant is selected
- **THEN** the banner SHALL read "Woohoo!" in pyfiglet slant font
- **AND** the headline SHALL be "It's all yours!"
- **AND** confetti-like ASCII characters (`.`, `*`, `+`, `o`) SHALL surround the banner
- **AND** the accent color SHALL be coral (`#ff6b6b`)

### Requirement: Variant 2 — Cozy
The "Cozy" variant SHALL use warm, relaxing visuals.

#### Scenario: Cozy variant renders
- **WHEN** the cozy variant is selected
- **THEN** the banner SHALL read "Me Time." in pyfiglet shadow font
- **AND** the headline SHALL be "Ready for your me-time."
- **AND** the body copy SHALL be "Your download is quietly settled and waiting for you."
- **AND** the accent color SHALL be sage green (`#4a5d4e`)

### Requirement: Variant 3 — Sensory
The "Sensory" variant SHALL use sleek, precise visuals with a checkmark.

#### Scenario: Sensory variant renders
- **WHEN** the sensory variant is selected
- **THEN** the banner SHALL read "Success!" in pyfiglet standard font
- **AND** a large ASCII checkmark (`/`) SHALL be displayed
- **AND** the headline SHALL be "Your treasure has arrived."
- **AND** the accent color SHALL be emerald green (`#10b981`)

### Requirement: Variant 4 — Gamified
The "Gamified" variant SHALL use humorous, pixel-art style visuals.

#### Scenario: Gamified variant renders
- **WHEN** the gamified variant is selected
- **THEN** the banner SHALL read "Mission Accomplished!" in pyfiglet bubble font
- **AND** a pixel-art style treasure chest or character SHALL be shown using ASCII
- **AND** the headline SHALL be "Our digital hamsters ran as fast as they could!"
- **AND** the body copy SHALL be "They are now taking a well-deserved nap."
- **AND** the accent color SHALL be amber (`#f59e0b`)

### Requirement: Action buttons
The completion screen SHALL provide three action buttons.

#### Scenario: Download Another button
- **WHEN** the user clicks "Download Another"
- **THEN** the completion screen SHALL be dismissed (pop)
- **AND** the main download screen SHALL be visible and ready for a new URL

#### Scenario: Open Folder button
- **WHEN** the user clicks "Open Folder"
- **THEN** the system SHALL open the output directory in the system file manager
- **AND** the completion screen SHALL remain displayed

#### Scenario: Quit button
- **WHEN** the user clicks "Quit"
- **THEN** the application SHALL exit

### Requirement: Download metrics tracking
The system SHALL track download start time and compute completion metrics.

#### Scenario: Download timing
- **WHEN** a download starts
- **THEN** the start time SHALL be recorded
- **WHEN** the download completes
- **THEN** the elapsed duration SHALL be computed as `end_time - start_time`
- **AND** the total bytes downloaded SHALL be retrieved from the output file
- **AND** the average speed SHALL be computed as `total_bytes / elapsed_seconds`

### Requirement: TMP_jable_bye variant
The system SHALL show a special "farewell" variant when the user quits after a completed download.

#### Scenario: Bye screen on quit
- **WHEN** the user clicks "Quit" on the completion screen
- **THEN** a brief "TMP_jable_bye" farewell screen SHALL display for 2 seconds before exiting
- **AND** it SHALL show a goodbye message and the pyfiglet "Bye!" banner
