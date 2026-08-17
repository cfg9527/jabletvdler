## ADDED Requirements

### Requirement: Save metadata after download
After every successful download, the system SHALL save the video's metadata to a JSON file in the `jable_db/` directory.

#### Scenario: Save metadata file
- **WHEN** a download completes successfully
- **THEN** the system writes `<video_code>.json` to `jable_db/` containing the full `VideoInfo` fields

#### Scenario: jable_db directory is created if missing
- **WHEN** a download completes and `jable_db/` does not exist
- **THEN** the system creates `jable_db/` before writing the metadata file

### Requirement: Metadata file format
The metadata JSON file SHALL include a `_version` field and all fields from `VideoInfo`.

#### Scenario: JSON contains version field
- **WHEN** a metadata file is written
- **THEN** the JSON SHALL contain a `"_version": 1` key

#### Scenario: JSON reflects VideoInfo fields
- **WHEN** a metadata file is read
- **THEN** every field from `VideoInfo` (code, title, full_title, actresses, tags, category, release_date, views, thumbnail, m3u8_url, video_id) SHALL be present

### Requirement: Tolerant JSON reader
The system SHALL read metadata JSON files that contain extra or unknown keys without error.

#### Scenario: Extra key ignored
- **WHEN** a JSON file contains keys not present in `VideoInfo`
- **THEN** the reader skips unknown keys and populates only known fields

### Requirement: Metadata update on re-download
If a metadata file already exists for a video code, the system SHALL overwrite it on re-download.

#### Scenario: Overwrite existing metadata
- **WHEN** a video is downloaded and `<code>.json` already exists in `jable_db/`
- **THEN** the existing file is overwritten with the current download's metadata

### Requirement: Metadata store location
The `jable_db/` directory SHALL be located at `<output_dir>/jable_db/`.

#### Scenario: Default output directory
- **WHEN** `JABLETV_DOWNLOAD_DIR` is not set
- **THEN** `jable_db/` resolves to `downloaded/jable_db/`

#### Scenario: Custom output directory
- **WHEN** `JABLETV_DOWNLOAD_DIR` is set to `/custom/path`
- **THEN** `jable_db/` resolves to `/custom/path/jable_db/`
