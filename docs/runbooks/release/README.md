# Release

This guide explains the release procedure using version 0.1.0 as an example.

## Release kiarina first

Development resolves kiarina from its git HEAD (`[tool.uv.sources]` in `pyproject.toml`),
so kiari can be using kiarina code that has never been released. The published wheel only
carries the `kiarina[all]>=X` specifier, so releasing kiari in that state ships a promise
that PyPI cannot satisfy.

Before releasing kiari:

1. Release kiarina-python, if kiari depends on anything newer than its latest release.
2. Raise the `kiarina[all]` floor in `pyproject.toml` to that released version.
3. Confirm the released combination actually works:

   ```sh
   uv sync --no-sources --all-extras --all-groups
   mise run ci
   uv sync --all-extras --all-groups   # restore the git HEAD environment
   ```

`release-pypi.yml` runs the same `--no-sources` check, so a floor that is still a lie fails
the tag build before anything is published. Running it locally first just saves the round
trip.

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
