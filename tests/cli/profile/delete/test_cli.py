import click
import pytest

from kiari.cli.profile.delete.cli import _delete
from kiari.core.profile import Profile, profile_store


@pytest.fixture(autouse=True)
def cleanup_profiles():
    yield
    profile_store.delete_all()


def test_nonexistent() -> None:
    with pytest.raises(click.ClickException, match="Profile not found"):
        _delete("nonexistent")


def test_current() -> None:
    with pytest.raises(click.ClickException, match="Cannot delete the current profile"):
        _delete("default")


def test_delete() -> None:
    profile_store.set_profile(Profile(name="dev"))
    profile_store.save_run_spec("dev", {"key": "value"})
    profile_store.save_config("dev", {"module": {"key": "value"}})

    _delete("dev")
