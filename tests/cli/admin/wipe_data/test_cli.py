from pathlib import Path

import pytest
from click.testing import CliRunner
from rich.console import Console

from kiari.cli.admin.wipe_data.cli import wipe_data


@pytest.fixture
def data_dir(tmp_path):
    return tmp_path / "data"


@pytest.fixture(autouse=True)
def setup(data_dir):
    from kiarina.utils.app import settings_manager

    settings_manager.cli_args = {"user_data_dir": str(data_dir)}
    yield
    settings_manager.cli_args = {}


def test_wipe_data(console: Console, data_dir: Path) -> None:
    (data_dir / "profiles.yaml").parent.mkdir(parents=True, exist_ok=True)
    (data_dir / "profiles.yaml").write_text("data\n")

    result = CliRunner().invoke(wipe_data, input="y\n")

    output = console.export_text()
    assert result.exit_code == 0
    assert "Wipe User Data" in output
    assert str(data_dir / "profiles.yaml") in output
    assert "Total: 1 files, 5 B" in output
    assert not data_dir.exists()


def test_wipe_data_confirm_enter_defaults_to_no(data_dir: Path) -> None:
    file_path = data_dir / "profiles.yaml"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("data\n")

    result = CliRunner().invoke(wipe_data, input="\n")

    assert result.exit_code == 0
    assert file_path.exists()


def test_wipe_data_confirm_yes_deletes(data_dir: Path) -> None:
    file_path = data_dir / "profiles.yaml"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("data\n")

    result = CliRunner().invoke(wipe_data, input="y\n")

    assert result.exit_code == 0
    assert not file_path.exists()


def test_wipe_data_force_deletes_without_confirmation(data_dir: Path) -> None:
    file_path = data_dir / "profiles.yaml"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("data\n")

    result = CliRunner().invoke(wipe_data, ["-f"])

    assert result.exit_code == 0
    assert not file_path.exists()
