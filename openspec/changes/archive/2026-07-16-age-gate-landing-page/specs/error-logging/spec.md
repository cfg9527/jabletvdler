## ADDED Requirements

### Requirement: Logging module
The system SHALL provide a centralized logging module at `jabletv/logger.py` that configures Python's standard `logging` framework.

#### Scenario: Logger module importable
- **WHEN** another module imports `from jabletv.logger import setup_logging, get_logger`
- **THEN** the import SHALL succeed without errors
- **AND** `setup_logging()` SHALL be callable to initialize logging
- **AND** `get_logger(name)` SHALL return a configured logger instance

### Requirement: Log directory
The system SHALL write log files to a `log/` directory created relative to the current working directory.

#### Scenario: Log directory creation
- **WHEN** `setup_logging()` is called
- **THEN** the `log/` directory SHALL be created if it does not exist
- **AND** the application SHALL NOT crash if the directory cannot be created (graceful fallback)

### Requirement: Application log file
The system SHALL write all INFO-level and above log messages to `log/app.log`.

#### Scenario: App log written
- **WHEN** any module logs a message at INFO, WARNING, ERROR, or CRITICAL level
- **THEN** the message SHALL appear in `log/app.log`
- **AND** the log entry SHALL include a timestamp, log level, logger name, and message
- **AND** the log entry format SHALL be: `[YYYY-MM-DD HH:MM:SS] LEVEL    logger.name: message`

### Requirement: Error log file
The system SHALL write all ERROR-level and above log messages to a separate `log/error.log` file.

#### Scenario: Error log separated
- **WHEN** any module logs a message at ERROR or CRITICAL level
- **THEN** the message SHALL appear in `log/error.log`
- **AND** the message SHALL also still appear in `log/app.log`
- **AND** WARNING and INFO messages SHALL NOT appear in `log/error.log`

### Requirement: Log rotation
The system SHALL rotate log files when they reach a maximum size to prevent unbounded disk usage.

#### Scenario: Log rotation configured
- **WHEN** a log file exceeds 5 MB
- **THEN** the file SHALL be rotated (renamed with a `.1`, `.2`, etc. suffix)
- **AND** at most 3 rotated backup files SHALL be kept
- **AND** the oldest backup SHALL be automatically deleted

### Requirement: Logging in app.py
The `app.py` module SHALL log application start, application exit, and any errors.

#### Scenario: App lifecycle logged
- **WHEN** the application starts
- **THEN** `app.py` SHALL log an INFO message: "JableTV Downloader starting"
- **WHEN** the application exits
- **THEN** `app.py` SHALL log an INFO message: "JableTV Downloader shutting down"
- **WHEN** an unhandled exception occurs
- **THEN** it SHALL be logged at ERROR level with traceback

### Requirement: Logging in downloader.py
The `downloader.py` module SHALL log download lifecycle and errors.

#### Scenario: Download events logged
- **WHEN** a download starts
- **THEN** an INFO message SHALL be logged with the video code
- **WHEN** a download completes successfully
- **THEN** an INFO message SHALL be logged with the output path
- **WHEN** a download fails or a segment download error occurs
- **THEN** the error SHALL be logged at ERROR level with details

### Requirement: Logging in scraper.py
The `scraper.py` module SHALL log scrape attempts and failures.

#### Scenario: Scrape events logged
- **WHEN** a scrape is attempted
- **THEN** an INFO message SHALL be logged with the URL
- **WHEN** a scrape succeeds
- **THEN** an INFO message SHALL be logged with the video code found
- **WHEN** a scrape fails
- **THEN** the error SHALL be logged at ERROR level
