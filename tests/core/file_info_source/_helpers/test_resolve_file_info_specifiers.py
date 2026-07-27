import pytest

from kiari.core.file_info_source import resolve_file_info_specifiers


@pytest.fixture
def setup_files(tmp_path):
    (tmp_path / "dir").mkdir()
    (tmp_path / "dir" / "a.txt").write_text("hello a")
    (tmp_path / "dir" / "b.txt").write_text("hello b")
    (tmp_path / "dir" / "c.log").write_text("hello c")


async def test_not_should_resolve() -> None:
    specifiers = await resolve_file_info_specifiers("{}")
    assert len(specifiers) == 1

    specifiers = await resolve_file_info_specifiers("gcs://bucket/path")
    assert len(specifiers) == 1


async def test_no_config(tmp_path, setup_files) -> None:
    specifiers = await resolve_file_info_specifiers(str(tmp_path / "dir" / "*.txt"))
    assert len(specifiers) == 2
    assert specifiers[0].endswith("a.txt")
    assert specifiers[1].endswith("b.txt")


async def test_config(tmp_path, setup_files) -> None:
    specifiers = await resolve_file_info_specifiers(
        str(tmp_path / "dir") + "?include=*.txt&exclude=b.txt&group=hello",
    )
    assert len(specifiers) == 1
    assert specifiers[0].endswith("a.txt?group=hello")
