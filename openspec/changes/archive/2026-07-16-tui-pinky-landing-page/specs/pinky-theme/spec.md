## ADDED Requirements

### Requirement: Theme color palette
The system SHALL define a centralized color palette matching the JableTV "sexy pinky" visual identity.

#### Scenario: Color constants defined
- **WHEN** the theme module is loaded
- **THEN** it SHALL define the following color constants:
  - Primary gradient start: `#91a5f4` (periwinkle blue)
  - Primary gradient end: `#b08cf9` (soft purple)
  - Accent hot pink: `#fe628e`
  - Secondary pink: `#ff6a88`
  - Coral: `#ff8382`
  - Surface dark: `#161a26`
  - Surface light: `#191d28`
  - Text primary: `#e0e0e0`
  - Text muted: `#8e9194`
  - Text secondary: `#b8babc`
  - Success green: `#1db954`

### Requirement: Textual theme application
The system SHALL apply the pinky color palette to the Textual app's CSS theme, overriding default Textual color variables.

#### Scenario: Theme overrides Textual CSS variables
- **WHEN** the app starts
- **THEN** `$primary` SHALL map to `#91a5f4`
- **AND** `$accent` SHALL map to `#fe628e`
- **AND** `$surface` SHALL map to `#161a26`
- **AND** `$error` SHALL map to `#ff8382`
- **AND** `$success` SHALL map to `#1db954`
- **AND** `$text-muted` SHALL map to `#8e9194`

### Requirement: Widget-specific styling
The system SHALL apply custom styling to each major widget type using the pinky palette.

#### Scenario: Header styling
- **WHEN** the Header widget is displayed
- **THEN** it SHALL have a dark background (`#161a26`)
- **AND** the title text SHALL be hot pink (`#fe628e`)
- **AND** the clock text SHALL be muted (`#8e9194`)

#### Scenario: Button styling
- **WHEN** a Button widget is rendered
- **THEN** primary buttons SHALL use the periwinkle-to-purple gradient background
- **AND** button hover state SHALL brighten the gradient
- **AND** button text SHALL be white

#### Scenario: Input styling
- **WHEN** an Input widget is rendered
- **THEN** it SHALL have a dark background (`#191d28`)
- **AND** border SHALL be muted grey (`#5e5d5a`)
- **AND** focus border SHALL be hot pink (`#fe628e`)
- **AND** cursor SHALL be hot pink

#### Scenario: Progress bar styling
- **WHEN** a ProgressBar widget is rendered
- **THEN** the bar fill SHALL use the hot pink color (`#fe628e`)
- **AND** the background track SHALL be dark (`#191d28`)

#### Scenario: Footer styling
- **WHEN** the Footer widget is displayed
- **THEN** it SHALL have a dark background (`#161a26`)
- **AND** key binding text SHALL be muted (`#8e9194`)
- **AND** highlighted key SHALL use hot pink (`#ff6a88`)

#### Scenario: Container borders
- **WHEN** a Container with border is rendered
- **THEN** the border SHALL use muted grey (`#5e5d5a`) by default
- **AND** focused containers SHALL use hot pink (`#fe628e`) border

### Requirement: Theme modularity
The theme SHALL be defined in a dedicated Python module so it can be imported and reused.

#### Scenario: Theme importable
- **WHEN** another module imports from `jabletv.themes`
- **THEN** it SHALL have access to `PinkyTheme` class with CSS property
- **AND** it SHALL have access to individual color constants
