import re

import click
import pytest
from rich.console import Console

from kiari.cli.profile.list.cli import (
    DEFAULT_COLUMNS,
    _build_table_caption,
    _filter_profiles,
    _format_config_path,
    _format_profile_file_cell,
    _list,
    _parse_columns,
    _sort_profiles,
)
from kiari.core.profile import Profile, profile_store


@pytest.fixture()
def cleanup_profiles():
    yield
    profile_store.delete_all()


def test_list_none(console: Console) -> None:
    _list(query="nonexistent")
    output = console.export_text()
    assert "No matching profiles found." in output


def test_list(console: Console, cleanup_profiles) -> None:
    profile_store.set_profile(Profile(name="dev"))
    profile_store.set_profile(Profile(name="prod"))

    _list()

    output = console.export_text()
    assert "dev" in output
    assert "prod" in output


def test_format_config_path(tmp_path) -> None:
    path = tmp_path / "config.yaml"
    text = _format_config_path(path)
    assert "(missing)" in text

    path.write_text("content")
    text = _format_config_path(path)
    assert "(missing)" not in text


def test_format_profile_file_cell(tmp_path) -> None:
    text = _format_profile_file_cell(tmp_path / "missing.txt", False)
    assert "(missing)" in text

    file_path = tmp_path / "file.txt"
    file_path.write_text("")

    text = _format_profile_file_cell(file_path, False)
    assert "Open" in text

    text = _format_profile_file_cell(file_path, True)
    assert "(empty)" in text

    file_path.write_text("Hello")
    text = _format_profile_file_cell(file_path, True)
    assert "Hello" in text


def test_parse_columns() -> None:
    assert _parse_columns(None) == DEFAULT_COLUMNS

    with pytest.raises(click.ClickException, match=re.escape("No columns specified.")):
        _parse_columns("")

    with pytest.raises(click.ClickException, match="Unknown columns"):
        _parse_columns("profile,unknown,description")

    assert _parse_columns("profile, description") == ("profile", "description")


def test_filter_profiles() -> None:
    profiles = [
        Profile(name="dev"),
        Profile(name="staging_1"),
        Profile(name="staging_2"),
        Profile(name="production"),
    ]
    assert _filter_profiles(profiles, None) == profiles
    assert len(_filter_profiles(profiles, "dev")) == 1
    assert len(_filter_profiles(profiles, "staging")) == 2


def test_sort_profiles() -> None:
    from datetime import datetime, timedelta

    profiles = [
        Profile(name="dev"),
        Profile(name="staging"),
        Profile(name="production"),
    ]
    profiles[0].updated_at = datetime.now()
    profiles[1].updated_at = datetime.now() - timedelta(days=1)
    profiles[2].updated_at = datetime.now() - timedelta(days=2)

    sorted_profiles = _sort_profiles(profiles, "name")
    assert sorted_profiles[0].name == "dev"
    assert sorted_profiles[1].name == "production"
    assert sorted_profiles[2].name == "staging"

    sorted_profiles = _sort_profiles(profiles, "updated")
    assert sorted_profiles[0].name == "dev"
    assert sorted_profiles[1].name == "staging"
    assert sorted_profiles[2].name == "production"


def test_build_table_caption() -> None:
    print(_build_table_caption(1, "dev", "dev", "name"))
