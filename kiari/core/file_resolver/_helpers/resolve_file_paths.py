from collections.abc import Sequence
from typing import Any

import httpx
from kiarina.agi.file import FilePath
from kiarina.agi.local_scanner import scan_pattern

from kiari.core.github import (
    GitHubPathPattern,
    GitHubPathSpec,
    fetch_github_dir,
    fetch_github_file,
    verify_github_trust,
)
from kiari.core.paths import get_github_cache_dir_path

from .._types.file_path_pattern import FilePathPattern


async def resolve_file_paths(
    source: FilePathPattern | Sequence[FilePathPattern],
) -> list[FilePath]:
    file_patterns = [source] if isinstance(source, str) else list(source)
    file_paths: list[FilePath] = []
    seen: set[FilePath] = set()

    for file_pattern in file_patterns:
        resolved_paths = await _resolve_file_path_pattern(file_pattern)

        for file_path in resolved_paths:
            if file_path in seen:
                continue

            file_paths.append(file_path)
            seen.add(file_path)

    return file_paths


async def _resolve_file_path_pattern(file_pattern: FilePathPattern) -> list[FilePath]:
    if file_pattern.startswith("@"):
        return await _resolve_github_path(file_pattern)

    return scan_pattern(file_pattern)


async def _resolve_github_path(
    github_path_pattern: GitHubPathPattern,
) -> list[FilePath]:
    github_path = GitHubPathSpec.from_string(github_path_pattern)

    if not await verify_github_trust(github_path):
        raise RuntimeError(f"Untrusted source: {github_path_pattern}. Execution cancelled.")

    github_kwargs: Any = {"cache_dir": get_github_cache_dir_path()}

    if github_path.is_dir:
        return await fetch_github_dir(github_path, **github_kwargs)

    try:
        file_path = await fetch_github_file(github_path, **github_kwargs)
        return [file_path]

    except (IsADirectoryError, httpx.HTTPStatusError) as e:
        if isinstance(e, httpx.HTTPStatusError) and e.response.status_code != 404:
            raise

        file_paths = await fetch_github_dir(github_path, **github_kwargs)

        if not file_paths:
            raise

        return file_paths
