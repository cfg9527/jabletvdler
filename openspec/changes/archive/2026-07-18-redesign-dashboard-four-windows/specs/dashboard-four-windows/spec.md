## ADDED Requirements

### Requirement: Four-window dashboard layout
The system SHALL display four equally-sized panes arranged in a 2×2 grid.
The system SHALL use border titles on each pane matching the app's TUI style.
The system SHALL use the screen's `BINDINGS` and `ENABLE_COMMAND_PALETTE` settings consistent with the existing dashboard.

#### Scenario: Layout renders four panes
- **WHEN** the dashboard screen is mounted
- **THEN** four bordered panes are visible in a 2×2 grid
- **THEN** each pane has a distinct border title

#### Scenario: Layout works on 80-column terminal
- **WHEN** the terminal width is 80 columns
- **THEN** all four panes are visible without horizontal scroll

### Requirement: Top Tags pane
The system SHALL display the top 5 most frequent tags in the first pane.
Tags SHALL be sorted by frequency in descending order.
Each row SHALL show the tag name and its count.

#### Scenario: Top Tags populated
- **WHEN** metadata contains videos with tags
- **THEN** the top-left pane shows up to 5 tags ranked by count

#### Scenario: Top Tags empty
- **WHEN** no videos have tags
- **THEN** the pane shows "No tags yet"

### Requirement: Top Titles pane
The system SHALL display the last 5 videos by date in the second pane.
Each row SHALL show the video code and title.
Videos with no date SHALL be sorted last.

#### Scenario: Top Titles populated
- **WHEN** metadata contains videos with dates
- **THEN** the top-right pane shows up to 5 most recent titles

#### Scenario: Top Titles empty
- **WHEN** no videos exist in metadata
- **THEN** the pane shows "No titles yet"

### Requirement: Top Actresses pane
The system SHALL display the top 5 actresses by video count in the third pane.
Actresses SHALL be sorted by video count in descending order.
Each row SHALL show the actress name and count.

#### Scenario: Top Actresses populated
- **WHEN** metadata contains videos with actresses
- **THEN** the bottom-left pane shows up to 5 actresses ranked by count

#### Scenario: Top Actresses empty
- **WHEN** no videos have actresses listed
- **THEN** the pane shows "No actresses yet"

### Requirement: Library Summary pane
The system SHALL display aggregate library statistics in the fourth pane.
The summary SHALL include: total videos, total unique tags, total unique actresses, and earliest/latest video date.

#### Scenario: Library Summary populated
- **WHEN** metadata contains videos
- **THEN** the bottom-right pane shows total videos, tag count, actress count, and date range

#### Scenario: Library Summary empty
- **WHEN** no videos exist
- **THEN** the pane shows "No data yet"

### Requirement: Empty library state
When `load_all_metadata()` returns zero entries, all four panes SHALL display their respective empty messages.
The screen SHALL remain usable with the Back button.

#### Scenario: Fresh install no data
- **WHEN** the library is empty
- **THEN** all four panes show empty-state messages
- **THEN** the Back button navigates to the previous screen
