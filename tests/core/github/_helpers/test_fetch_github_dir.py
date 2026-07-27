# TODO: kiari 公開後にテストデータを改善する
from kiari.core.github import GitHubPathSpec, fetch_github_dir


async def test_github_path_pattern(tmp_path) -> None:
    file_paths = await fetch_github_dir(
        "@kiarina/pydantic-settings-manager/.vscode",
        cache_dir=tmp_path,
    )
    assert len(file_paths) > 0


async def test_github_path_spec(tmp_path) -> None:
    file_paths = await fetch_github_dir(
        GitHubPathSpec.from_string("@kiarina/pydantic-settings-manager/.vscode"),
        cache_dir=tmp_path,
    )
    assert len(file_paths) > 0


async def test_cache(tmp_path) -> None:
    await fetch_github_dir("@kiarina/pydantic-settings-manager/.vscode", cache_dir=tmp_path)
    await fetch_github_dir(
        "@kiarina/pydantic-settings-manager/.vscode", cache_dir=tmp_path
    )  # cache


async def test_include_exclude_patterns(tmp_path) -> None:
    file_paths = await fetch_github_dir(
        GitHubPathSpec.from_string(
            "@kiarina/pydantic-settings-manager/.vscode?include=*.json&exclude=launch.json",
        ),
        cache_dir=tmp_path,
    )
    assert len(file_paths) > 0
