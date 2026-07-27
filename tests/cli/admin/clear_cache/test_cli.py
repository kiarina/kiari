from pathlib import Path

import pytest
from click.testing import CliRunner
from rich.console import Console

from kiari.cli.admin.clear_cache.cli import clear_cache


@pytest.fixture
def cache_dir(tmp_path):
    return tmp_path / "cache"


@pytest.fixture(autouse=True)
def setup(cache_dir):
    from kiarina.utils.app import settings_manager

    settings_manager.cli_args = {"user_cache_dir": str(cache_dir)}
    yield
    settings_manager.cli_args = {}


def test_clear_cache(console: Console, cache_dir: Path) -> None:
    (cache_dir / "github_files" / "repo.txt").parent.mkdir(parents=True, exist_ok=True)
    (cache_dir / "github_files" / "repo.txt").write_text("cache\n")

    result = CliRunner().invoke(clear_cache, input="y\n")

    output = console.export_text()
    assert result.exit_code == 0
    assert "Clear Cache Data" in output
    assert str(cache_dir / "github_files" / "repo.txt") in output
    assert "Total: 1 files, 6 B" in output
    assert not cache_dir.exists()


def test_clear_cache_confirm_enter_defaults_to_no(cache_dir: Path) -> None:
    file_path = cache_dir / "github_files" / "repo.txt"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("cache\n")

    result = CliRunner().invoke(clear_cache, input="\n")

    assert result.exit_code == 0
    assert file_path.exists()


def test_clear_cache_confirm_yes_deletes(cache_dir: Path) -> None:
    file_path = cache_dir / "github_files" / "repo.txt"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("cache\n")

    result = CliRunner().invoke(clear_cache, input="y\n")

    assert result.exit_code == 0
    assert not file_path.exists()


def test_clear_cache_force_deletes_without_confirmation(cache_dir: Path) -> None:
    file_path = cache_dir / "github_files" / "repo.txt"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("cache\n")

    result = CliRunner().invoke(clear_cache, ["--force"])

    assert result.exit_code == 0
    assert not file_path.exists()
