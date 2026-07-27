import os
from pathlib import Path

import httpx
from kiarina.agi.file import FilePath
from kiarina.agi.local_scanner import scan_directory

from .._models.github_path_spec import GitHubPathSpec
from .._settings import settings_manager
from .._types.github_path_pattern import GitHubPathPattern
from .fetch_github_file import fetch_github_file


async def fetch_github_dir(
    github_path: GitHubPathPattern | GitHubPathSpec,
    *,
    cache_dir: Path | str,
    ignore_cache: bool | None = None,
) -> list[FilePath]:
    settings = settings_manager.get_settings()

    if ignore_cache is None:
        ignore_cache = settings.ignore_cache

    if isinstance(github_path, str):
        spec = GitHubPathSpec.from_string(github_path)
    else:
        spec = github_path

    cache_path = spec.get_cache_path(cache_dir)

    if cache_path.is_dir() and not ignore_cache:
        return scan_directory(
            str(cache_path),
            include_patterns=spec.include_patterns,
            exclude_patterns=spec.exclude_patterns,
        )

    tree_github_paths = await _fetch_github_tree_items(spec)

    if spec.include_patterns or spec.exclude_patterns:
        tree_github_paths = _filter_github_paths(
            tree_github_paths,
            include_patterns=spec.include_patterns,
            exclude_patterns=spec.exclude_patterns,
        )

    local_file_paths: list[FilePath] = []

    for tree_github_path in tree_github_paths:
        local_file_path = await fetch_github_file(
            tree_github_path,
            cache_dir=cache_dir,
            ignore_cache=ignore_cache,
        )
        local_file_paths.append(local_file_path)

    return local_file_paths


async def _fetch_github_tree_items(spec: GitHubPathSpec) -> list[GitHubPathSpec]:
    settings = settings_manager.get_settings()

    headers = {"Accept": "application/vnd.github+json"}

    if settings.access_token:
        headers["Authorization"] = f"token {settings.access_token.get_secret_value()}"
    elif github_token := os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"token {github_token}"

    async with httpx.AsyncClient() as client:
        response = await client.get(spec.trees_api_url, headers=headers)
        response.raise_for_status()
        data = response.json()

    prefix = f"{spec.dir_path}/" if spec.dir_path else ""

    result: list[GitHubPathSpec] = []

    for item in data.get("tree", []):
        if item["type"] != "blob":
            continue

        item_path: str = item["path"]

        if not item_path.startswith(prefix):
            continue

        result.append(
            GitHubPathSpec(
                username=spec.username,
                repo=spec.repo,
                file_path=item_path,
                commit_hash=spec.commit_hash,
            )
        )

    return result


def _filter_github_paths(
    specs: list[GitHubPathSpec],
    *,
    include_patterns: list[str] | None,
    exclude_patterns: list[str] | None,
) -> list[GitHubPathSpec]:
    filtered: list[GitHubPathSpec] = []

    for spec in specs:
        rel_path = Path(spec.file_path)

        if exclude_patterns:
            if any(
                rel_path.match(pattern) or Path(rel_path.name).match(pattern)
                for pattern in exclude_patterns
            ):
                continue

        if include_patterns:
            if not any(
                rel_path.match(pattern) or Path(rel_path.name).match(pattern)
                for pattern in include_patterns
            ):
                continue

        filtered.append(spec)

    return filtered
