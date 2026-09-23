# kiarina-python Docs Sync Playbook

Use this playbook to keep `docs/concepts/kiarina-python/` aligned with the versions of
kiarina-python that kiari actually uses.

**Trigger:** a `make upgrade` or `uv lock --upgrade` changes any `kiarina-*` package.
Detect relevant lock changes with:

```sh
git diff uv.lock | grep -B2 '^[-+]version' | grep -A2 'kiarina'
```

Because kiarina-python changes frequently, an upgrade commit must either complete this
playbook or record the outstanding sync as a file under `tasks/`.

## 1. Detect Version Drift

Read the locked versions:

```sh
awk '/^\[\[package\]\]/{p=1} p&&/^name = /{n=$3} p&&/^version = /{if(n ~ /kiarina/) print n, $3; p=0}' uv.lock
```

Compare them with [Documented Versions](../concepts/kiarina-python/overview.md#documented-versions).
If every version matches, the sync is complete.

## 2. Review Changes

For each package with drift, inspect the local
`~/src/github.com/kiarina/kiarina-python` checkout and update it first if necessary.

1. Read the root and package-specific changelogs from the documented version through the
   locked version.
2. Inspect affected public `__init__.py` exports when an API may have changed.
3. Identify breaking changes, renames, and new features that affect kiari documentation.

## 3. Update Documentation

- Update affected documents under `docs/concepts/kiarina-python/`.
- Add new packages and modules to the reverse lookup in `overview.md`.
- Update the Documented Versions table only after the corresponding content has been
  reviewed and corrected. The table means “documentation is current through this version.”

## 4. Record Follow-Up Work

- Put reusable knowledge in the relevant document.
- Put unresolved breaking changes or required kiari code changes in a `tasks/` file,
  and add a pointer line to the task list in `AGENTS.md`.
