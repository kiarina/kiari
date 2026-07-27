# Release

This guide explains the release procedure using version 0.1.0 as an example.

## Release Procedure

### 1. Update CHANGELOG

Add your changes to the `[Unreleased]` section in `CHANGELOG.md`.

### 2. Update Version and CHANGELOG

```sh
mise run pyproject:bump-version 0.1.0
mise run changelog:bump-version 0.1.0
```

### 3. Run CI Checks

```sh
mise run ci
```

### 4. Commit, Tag, and Push

```sh
git add pyproject.toml CHANGELOG.md uv.lock
git commit -m "chore: release v0.1.0"
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin main --tags
```

## Automated Publication

Pushing a tag such as `v0.1.0` runs `.github/workflows/release-pypi.yml`, creates a GitHub Release, and publishes to PyPI through Trusted Publishing.

Configure PyPI Trusted Publishing with:

- Project name: `kiari`
- Owner: `kiarina`
- Repository: `kiari`
- Workflow: `.github/workflows/release-pypi.yml`
- Environment: `pypi`

## Manual Publication

Manual publication uses the local PyPI API token available to `uv publish`.

```sh
mise run build
mise run publish
```
