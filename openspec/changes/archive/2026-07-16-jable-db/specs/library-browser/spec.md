## ADDED Requirements

### Requirement: Library screen exists
The TUI SHALL have a screen that lists all downloaded videos from `jable_db/`.

#### Scenario: Open library screen
- **WHEN** the user navigates to the library screen
- **THEN** all entries from `jable_db/` are loaded and displayed in a list

#### Scenario: Empty state
- **WHEN** the library screen opens and `jable_db/` is empty or missing
- **THEN** the screen SHALL display an "No downloaded videos found" message

### Requirement: Library entries display
Each entry in the library list SHALL show the video code, title, actresses, and tags.

#### Scenario: Entry details shown
- **WHEN** the library list is populated
- **THEN** each entry displays the video code, title, actresses (comma-separated), and tags

### Requirement: Search by code
The library screen SHALL allow the user to filter the list by video code.

#### Scenario: Code search
- **WHEN** the user types in the search input
- **THEN** the list filters to show only entries whose code contains the search text (case-insensitive)

### Requirement: Search by tag
The library screen SHALL allow the user to filter the list by tag.

#### Scenario: Tag search
- **WHEN** the user searches for a tag name
- **THEN** the list filters to show only entries whose tags include the search text (case-insensitive)

### Requirement: Search by actress
The library screen SHALL allow the user to filter the list by actress name.

#### Scenario: Actress search
- **WHEN** the user searches for an actress name
- **THEN** the list filters to show only entries whose actresses include the search text (case-insensitive)

### Requirement: Search by category
The library screen SHALL allow the user to filter the list by category.

#### Scenario: Category search
- **WHEN** the user searches for a category name
- **THEN** the list filters to show only entries whose category includes the search text (case-insensitive)

### Requirement: View video details
The library screen SHALL allow the user to select an entry and view its full metadata.

#### Scenario: Show details on select
- **WHEN** the user selects an entry in the library list
- **THEN** the screen displays the full metadata (all `VideoInfo` fields) for that video

### Requirement: Open video URL from library
The library screen SHALL allow the user to open the original video URL for a selected entry.

#### Scenario: Open URL
- **WHEN** the user presses a key/button to open the URL for a selected entry
- **THEN** the system opens `https://jable.tv/videos/<code>/` in the default browser
