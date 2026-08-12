# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added

- Added GCS and Firebase Storage `HistoryRepository` implementations with
  RunContext-scoped object name templates. GCS uses backend credentials directly;
  Firebase Storage supports static or refreshable client ID tokens.
- Exposed `run_schedule` as the public API of `kiari.cli.schedule` (moved from
  `_operations/` to `_helpers/`) so embedding runtimes can import it without touching
  private paths.
- Added optional `stop_event` injection to `run_schedule` and `graceful_shutdown` so an
  embedding runtime can stop the schedule loop externally; the in-flight request completes
  before the loop exits.

### Changed

- Updated the Chrome tool to Chrome Bridge SDK 0.4.x, including browser-dialog page
  states and explicit accept/dismiss responses.
- Delayed Pub/Sub acknowledgement until watch handler completion and released messages for
  redelivery after processing failures.

## [0.1.0] - 2026-07-10

### Added

- Initial release of the `kiari` package.
- Added GitHub Actions CI and PyPI Trusted Publishing release workflow.
