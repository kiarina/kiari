# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Changed

- Updated the Chrome tool to Chrome Bridge SDK 0.4.x, including browser-dialog page
  states and explicit accept/dismiss responses.
- Allowed schedule and watch handlers to override request execution without invoking the
  agent engine.
- Delayed Pub/Sub acknowledgement until watch handler completion and released messages for
  redelivery after processing failures.

## [0.1.0] - 2026-07-10

### Added

- Initial release of the `kiari` package.
- Added GitHub Actions CI and PyPI Trusted Publishing release workflow.
