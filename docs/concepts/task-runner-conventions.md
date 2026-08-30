# Task Runner Conventions

This document defines how kiari divides responsibilities between mise tasks and Make.

## Principles

- Put all task logic in scripts under `.mise/tasks/`. Tasks may accept arguments and
  flags.
- Keep the Makefile as a thin entry point. Development targets delegate to
  `mise run <task>`; only dependency inspection and synchronization call uv directly.
- GitHub Actions also invokes mise tasks directly.

## mise Tasks

Store each task as a Bash script under `.mise/tasks/`.

- Add `#MISE description=...` and any required `#USAGE` declarations.
- Use `set -euo pipefail`.
- Build commands with Bash arrays rather than string concatenation and `eval`.
- Group related tasks into directory namespaces, such as
  `changelog/extract` → `mise run changelog:extract`.

| Task | Responsibility |
| --- | --- |
| `setup` | Install mise tools, dependencies, and test assets |
| `format` | Run Ruff fixes and formatting; modifies code |
| `lint` | Run Ruff checks, formatting checks, and mypy without modifying files |
| `test` | Run pytest with optional coverage, costly, verbose, and path flags |
| `ci` | Run lint, tests with coverage, and build |
| `build` / `publish` | Build and publish the package |
| `changelog:*` / `pyproject:*` | Perform release version operations |
| `test-assets:*` / `test-settings:*` | Manage shared assets and encrypted settings |

Ruff checks `kiari/` and `tests/`. mypy checks `kiari/` in strict mode. Only
`format` applies automatic changes.

## Makefile

The Makefile offers familiar daily entry points and follows the kiarina-python target
layout.

- Development targets call their corresponding mise task.
- `list`, `update`, and `upgrade` call uv directly for dependency inspection and sync.
- `check`, the default target, runs format and then lint.
- Make targets do not accept general arguments; call mise directly when flags are needed.
- A thin dedicated target may fix a path and flags for an environment-specific test.
  `chrome_test` is the real Chrome Bridge example.
- Do not add shell branching or other workflow logic to recipes.

## Choosing an Entry Point

```sh
make                         # format, then lint
make ci                      # lint, test with coverage, then build
mise run ci                  # same CI sequence
mise run test --costly       # call mise directly when flags are needed
make chrome_test             # real Chrome Bridge integration test
```
