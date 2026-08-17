## ADDED Requirements

### Requirement: Age gate display on startup
The system SHALL display an 18+ age verification gate as the first screen when the application starts, before showing the main download interface.

#### Scenario: Age gate appears before main UI
- **WHEN** the user runs `python -m jabletv`
- **THEN** the application SHALL display the age gate screen covering the entire terminal
- **AND** the main download interface SHALL NOT be visible until the user clicks "Yes, I am 18+"

#### Scenario: Age gate content
- **WHEN** the age gate is displayed
- **THEN** it SHALL contain ASCII art reading "JABLETV_DL"
- **AND** a dual-language age warning in English and Japanese
- **AND** a "Yes, I am 18+" button
- **AND** a "No" button

### Requirement: ASCII art header
The age gate SHALL display "JABLETV_DL" in large block ASCII art as the header.

#### Scenario: JABLETV_DL ASCII displayed
- **WHEN** the age gate renders
- **THEN** the word "JABLETV_DL" SHALL be rendered in prominent ASCII block letters
- **AND** it SHALL be center-aligned at the top of the screen
- **AND** it SHALL NOT animate or cycle through frames (static display)

### Requirement: Age warning text
The age gate SHALL display an age consent warning in both English and Japanese.

#### Scenario: English warning displayed
- **WHEN** the age gate renders
- **THEN** the following English text SHALL be visible: "WARNING: This site contains adult content. You must be at least 18 years old to enter. By entering, you confirm that you are of legal age."

#### Scenario: Japanese warning displayed
- **WHEN** the age gate renders
- **THEN** the following Japanese text SHALL be visible below the English text: "警告：このサイトには成人向けコンテンツが含まれています。入場するには18歳以上である必要があります。入場することにより、あなたが法的な成人年齢（18歳以上）であることを確認したことになります。"

### Requirement: "Yes, I am 18+" button
The age gate SHALL provide a "Yes, I am 18+" button that proceeds to the main application.

#### Scenario: Yes button navigates to main app
- **WHEN** the user clicks the "Yes, I am 18+" button
- **THEN** the age gate SHALL be dismissed
- **AND** the main download screen SHALL become visible and interactive
- **AND** all download functionality SHALL be available

### Requirement: "No" exit button
The age gate SHALL provide a "No" button that exits the application immediately.

#### Scenario: No button exits
- **WHEN** the user clicks the "No" button
- **THEN** the application SHALL exit immediately with return code 0
- **AND** the main download screen SHALL NOT be shown

### Requirement: Visual styling
The age gate SHALL use the pinky theme colors (DeepPink accents, dark background, periwinkle gradient) consistent with the rest of the application.

#### Scenario: Pinky theme applied
- **WHEN** the age gate renders
- **THEN** the background SHALL be `#161a26` (surface dark)
- **AND** the "Yes" button SHALL use hot pink (`#fe628e`) accent
- **AND** the "No" button SHALL use a muted grey color
- **AND** the ASCII art SHALL be rendered in DeepPink (`#ff1493`)
