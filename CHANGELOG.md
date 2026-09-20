# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [0.3.0] - 2026-09-20

### Added

- Added the `history_compact` tool to replace prior events with a compact context,
  narrative, and referenced-file-path checkpoint while preserving the current tool
  call/result pair.
- Added the `text_file_purge` tool to remove multiple text `FileInfo` values from
  History by ID without deleting underlying assets or caches.
- Exposed `run_watch` as the public API of `kiari.cli.watch` (moved from `_operations/`
  to `_helpers/`) so embedding runtimes can import it without touching private paths.
- Added optional `stop_event` injection to `run_watch` so an embedding runtime can stop
  the watch loop externally; queued events are drained before the loop exits.

### Changed (BREAKING)

- `RTDBWatcher` emits the whole current value of the watched path each time it changes,
  following `kiarina-lib-firebase-rtdb` 2.29.0, whose `watch_data` yields values instead of
  raw `put` / `patch` events. `RTDBWatchPayload` drops `event_type`, `path` is now the
  watched path, and `data` is its current value (`None` while the path does not exist).
- Renamed `RunOptions.time_zone` and the profile key `time_zone` to `timezone`, and
  renamed the CLI option `--time-zone` to `--timezone`. This follows the corresponding
  breaking rename in `kiarina-agi-base`'s `RunContext` and `RunContextSettings`.
- Resolved the Firebase Storage `HistoryRepository`'s ID token through `token_manager_registry`,
  the same way `RTDBWatcher` already does. `create_firebase_storage_history_repository` no longer
  takes `token_provider`, the `id_token` setting is replaced by `firebase_settings_key`, and the
  token is refreshed by the `TokenManager` instead of being pushed in from outside. A client that
  only holds an ID token, with no refresh token, can no longer supply it directly.

### Changed

- Resolved kiarina from the HEAD of its default branch instead of PyPI during development,
  so a change made in kiarina-python can be evaluated here before it is released. The
  published wheel is unaffected: it still carries the `kiarina[all]` specifier, and
  `release-pypi.yml` now re-resolves with `--no-sources` and runs the full CI against the
  newest released kiarina, so a tag fails rather than publishing a floor that PyPI cannot
  satisfy.

- Required kiarina 2.32.0 or later, and took the released 2.32.0 as the development
  baseline. `History` now carries a `memory_graph` (2.31.0 replaced `History.embeddings`),
  asset caches no longer expire by default (2.32.0), and the RTDB watcher can share an
  `RTDBMirror` (2.30.x). kiari uses none of the removed APIs directly.

- Required kiarina 2.27.0 or later. `kiarina.lib.firebase` renamed `TokenData` to `Token`,
  froze it, and now derives `project_id` / `uid` / `expires_at` from the `id_token` claims,
  so a token set is constructed from the refresh token and ID token alone. The RTDB watcher
  still resolves its `TokenManager` through `token_manager_registry` and needs no change.
- The Firebase token file path setting is now `token_file_path`
  (`KIARINA_LIB_FIREBASE_TOKEN_FILE_PATH`), renamed from `token_data_file_path`
  (`KIARINA_LIB_FIREBASE_TOKEN_DATA_FILE_PATH`).

### Fixed

- Made the release workflow's released-dependency gate actually hold. `release-pypi.yml`
  synced with `--no-sources`, but `mise run ci` runs the tests through `uv run`, which
  re-syncs from `uv.lock` and reinstalled kiarina from its git HEAD, so the gate checked
  the very thing it was meant to exclude. The job now sets `UV_NO_SOURCES=1` for every uv
  command.

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
