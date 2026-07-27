# TODO: kiari 公開後にテストデータを改善する
from pathlib import Path

import pytest

from kiari.core.github import GitHubPathSpec, fetch_github_dir, fetch_github_file


async def test_github_path_pattern(tmp_path) -> None:
    file_path = await fetch_github_file(
        "@kiarina/kiarina-python/README.md",
        cache_dir=tmp_path,
    )
    assert Path(file_path).exists()


async def test_github_path_spec(tmp_path) -> None:
    file_path = await fetch_github_file(
        GitHubPathSpec.from_string("@kiarina/kiarina-python/README.md"),
        cache_dir=tmp_path,
    )
    assert Path(file_path).exists()


async def test_is_a_directory_error(tmp_path) -> None:
    await fetch_github_dir("@kiarina/pydantic-settings-manager/.vscode", cache_dir=tmp_path)
    with pytest.raises(IsADirectoryError):
        await fetch_github_file("@kiarina/pydantic-settings-manager/.vscode", cache_dir=tmp_path)


async def test_cache(tmp_path) -> None:
    await fetch_github_file("@kiarina/kiarina-python/README.md", cache_dir=tmp_path)
    await fetch_github_file("@kiarina/kiarina-python/README.md", cache_dir=tmp_path)  # cache
