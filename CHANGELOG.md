# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [0.2.0] - 2026-08-21

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

- Required kiarina 2.25.0 or later, and resolved the RTDB watcher's Firebase ID token
  through `token_manager_registry`. `RTDBWatcher` no longer builds its own `TokenManager`,
  and `KIARI2_WATCHER_RTDB_TOKEN_DATA_FILE_PATH` is replaced by the `token_data_file_path`
  setting of `kiarina.lib.firebase` (`KIARINA_LIB_FIREBASE_TOKEN_DATA_FILE_PATH`).
- Updated the Chrome tool to Chrome Bridge SDK 0.4.x, including browser-dialog page
  states and explicit accept/dismiss responses.
- Delayed Pub/Sub acknowledgement until watch handler completion and released messages for
  redelivery after processing failures.
- Refreshed every dependency to its latest compatible release, bringing Pillow to 12.3.0
  and closing the open Pillow security advisories.
- Bumped `jdx/mise-action` to 4.2.5 in the CI and release workflows.

### Removed

- Removed `FileTokenCache` from `kiari.impl.watcher_impl.rtdb`; `FileTokenStore` in
  `kiarina.lib.firebase` replaces it.

## [0.1.0] - 2026-07-10

### Added

- Initial release of the `kiari` package.
- Added GitHub Actions CI and PyPI Trusted Publishing release workflow.
