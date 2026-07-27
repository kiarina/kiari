import pytest

from kiari.core.file_resolver import resolve_file_paths


async def test_file_path_pattern(tmp_path) -> None:
    (tmp_path / "file1.txt").write_text("file1")
    (tmp_path / "file2.txt").write_text("file2")

    file_paths = await resolve_file_paths(str(tmp_path / "*.txt"))
    assert len(file_paths) == 2


async def test_github_path_pattern(tmp_path) -> None:
    file_paths = await resolve_file_paths("@kiarina/kiarina-python/README.md")
    assert len(file_paths) == 1


async def test_not_verify_trust(monkeypatch) -> None:
    async def mock_verify_trust(github_path):
        return False

    monkeypatch.setattr(
        "kiari.core.file_resolver._helpers.resolve_file_paths.verify_github_trust",
        mock_verify_trust,
    )

    with pytest.raises(RuntimeError, match="Untrusted source"):
        await resolve_file_paths("@kiarina/kiarina-python/README.md")


async def test_github_dir() -> None:
    file_paths = await resolve_file_paths("@kiarina/pydantic-settings-manager/.vscode/")
    assert len(file_paths) > 0


async def test_github_dir_as_file() -> None:
    file_paths = await resolve_file_paths("@kiarina/pydantic-settings-manager/.vscode")
    assert len(file_paths) > 0


async def test_resolve_file_paths_deduplicates(tmp_path) -> None:
    (tmp_path / "keep.txt").write_text("keep")

    file_paths = await resolve_file_paths([str(tmp_path / "*.txt"), str(tmp_path / "keep.txt")])

    assert file_paths == [str((tmp_path / "keep.txt").resolve())]
