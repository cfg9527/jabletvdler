## MODIFIED Requirements

### Requirement: Landing screen display
**Previous**: The system displayed a full-screen landing page with animated ASCII art that auto-dismissed on any key press.
**New**: The system SHALL display a full-screen age verification gate when the application starts, replacing the previous decorative landing screen.

The age gate SHALL NOT auto-dismiss on any key press — the user MUST explicitly click "Yes, I am 18+" to proceed.

#### Scenario: Age gate replaces decorative splash
- **WHEN** the application starts
- **THEN** the age verification gate SHALL be displayed (not the decorative animated splash)
- **AND** pressing an arbitrary key SHALL NOT dismiss the gate
- **AND** clicking anywhere on the screen SHALL NOT dismiss the gate
- **AND** only clicking the "Yes, I am 18+" button SHALL dismiss the gate

### Requirement: ASCII art content
**Previous**: The system displayed animated frames of a "JableTV" logo with a play button motif, cycling every 280ms.
**New**: The system SHALL display static ASCII art reading "JABLETV_DL" in large block letters. No animation or frame cycling SHALL occur.

#### Scenario: Static JABLETV_DL ASCII
- **WHEN** the gate is displayed
- **THEN** the ASCII art SHALL read "JABLETV_DL" in large block letters
- **AND** it SHALL be static (no frame cycling)
- **AND** there SHALL be exactly 1 frame (not 3+)

### Requirement: Dismissal behavior
**Previous**: The landing screen dismissed on any key press or mouse click.
**New**: The gate SHALL require explicit button interaction. Key press or click anywhere on the screen SHALL NOT dismiss the gate.

#### Scenario: No auto-dismissal
- **WHEN** the age gate is displayed
- **AND** the user presses a keyboard key
- **THEN** the gate SHALL remain displayed
- **AND** nothing SHALL happen

#### Scenario: Yes button dismisses
- **WHEN** the age gate is displayed
- **AND** the user clicks "Yes, I am 18+"
- **THEN** the gate SHALL be dismissed
- **AND** the main download interface SHALL appear

#### Scenario: No button exits
- **WHEN** the age gate is displayed
- **AND** the user clicks "No"
- **THEN** the application SHALL exit immediately

## REMOVED Requirements

### Requirement: ASCII art animation
**Reason**: Replaced by static "JABLETV_DL" ASCII art. Age gate no longer uses animated frames.
**Migration**: Remove `FRAMES` list, `_timer_handle`, `set_interval`, `_next_frame`, and `_update_frame` methods from `LandingScreen`.

### Requirement: Frame cycling timer
**Reason**: Age gate is a static screen — no timer-driven animation needed.
**Migration**: Remove `set_interval(0.28, ...)` call and all timer-related code from `on_mount`.

### Requirement: Key press and mouse click dismissal
**Reason**: Age gate requires explicit button interaction for legal compliance. Auto-dismiss on any key/click undermines the age verification purpose.
**Migration**: Remove `on_key` and `on_click` handlers from `LandingScreen`. Replace with button-based navigation.
