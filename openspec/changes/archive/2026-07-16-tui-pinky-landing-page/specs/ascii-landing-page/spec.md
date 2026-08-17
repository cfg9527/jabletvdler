## ADDED Requirements

### Requirement: Landing screen display
The system SHALL display a full-screen landing page when the application starts, before showing the main download interface.

#### Scenario: App starts with landing screen
- **WHEN** the user runs `python -m jabletv`
- **THEN** the application SHALL display the landing screen covering the entire terminal
- **AND** the main download interface SHALL NOT be visible until dismissed

#### Scenario: Landing screen content
- **WHEN** the landing screen is displayed
- **THEN** it SHALL contain animated ASCII art
- **AND** a title or tagline
- **AND** a prompt to press any key to continue

### Requirement: ASCII art animation
The system SHALL display animated ASCII art on the landing screen that cycles through multiple frames, creating a visual GIF-like effect.

#### Scenario: Frame cycling
- **WHEN** the landing screen is mounted
- **THEN** the ASCII art SHALL change to the next frame every 250-300ms
- **AND** SHALL loop continuously until dismissed

#### Scenario: Minimum frame count
- **WHEN** the landing screen is displayed
- **THEN** there SHALL be at least 3 distinct ASCII art frames
- **AND** each frame SHALL be visually different (not just a cursor blink)

### Requirement: Landing screen dismissal
The system SHALL dismiss the landing screen and transition to the main download interface when the user presses any key.

#### Scenario: Key press dismissal
- **WHEN** the landing screen is displayed
- **AND** the user presses any keyboard key
- **THEN** the landing screen SHALL be removed
- **AND** the main download interface SHALL become visible and focused

#### Scenario: Mouse click dismissal
- **WHEN** the landing screen is displayed
- **AND** the user clicks anywhere on the screen
- **THEN** the landing screen SHALL be removed
- **AND** the main download interface SHALL become visible and focused

### Requirement: Landing screen visual style
The landing screen SHALL use the "sexy pinky" color scheme (hot pink accent, dark background, periwinkle-purple gradient) consistent with the main app theme.

#### Scenario: Color consistency
- **WHEN** the landing screen is displayed
- **THEN** its colors SHALL match the pinky theme defined in the theme module
- **AND** the ASCII art SHALL be rendered in the accent hot pink color (#fe628e)
- **AND** the background SHALL be #161a26

### Requirement: No functional impact on download workflow
The landing screen SHALL NOT alter or interfere with the existing download functionality.

#### Scenario: Download works after dismissal
- **WHEN** the landing screen is dismissed
- **AND** the main interface is displayed
- **THEN** the existing URL input, download button, progress bar, metadata display, and log SHALL all function identically to their pre-change behavior
