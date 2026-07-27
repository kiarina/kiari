from collections.abc import Generator

import pytest
from kiarina.utils.app import settings_manager

from kiari.core.profile import Profile, profile_store


@pytest.fixture(autouse=True)
def clear_app_settings() -> Generator[None, None, None]:
    yield
    settings_manager.cli_args = {}


@pytest.fixture(autouse=True)
def cleanup_profile():
    yield
    profile_store.delete_all()


def test_file_path() -> None:
    print(f"file_path: {profile_store.file_path}")


# --------------------------------------------------
# Current Profile Name
# --------------------------------------------------


def test_get_current() -> None:
    assert profile_store.get_current() == "default"


def test_set_current() -> None:
    profile_store.set_current("dev")
    assert profile_store.get_current() == "dev"


# --------------------------------------------------
# Profiles
# --------------------------------------------------


def test_list_profiles() -> None:
    profiles = profile_store.list_profiles()
    assert len(profiles) == 1
    assert profiles[0].name == "default"


def test_get_profile() -> None:
    assert profile_store.get_profile().name == "default"
    assert profile_store.get_profile("default").name == "default"
    assert profile_store.get_profile("nonexistent").name == "nonexistent"


def test_has_profile() -> None:
    assert profile_store.has_profile("default") is True
    assert profile_store.has_profile("nonexistent") is False

    profile_store.set_profile(Profile(name="dev"))
    assert profile_store.has_profile("dev") is True


def test_set_profile() -> None:
    profile_store.set_profile(Profile(name="dev"))
    assert profile_store.get_profile("dev").name == "dev"


def test_delete_profile() -> None:
    profile_store.delete_profile("nonexistent")

    profile_store.set_profile(Profile(name="dev"))
    profile_store.delete_profile("dev")


# --------------------------------------------------
# Run Spec
# --------------------------------------------------


def test_load_run_spec() -> None:
    run_spec = profile_store.load_run_spec("default")
    assert run_spec == {}


def test_save_run_spec() -> None:
    profile_store.save_run_spec("default", {"key": "value"})
    run_spec = profile_store.load_run_spec("default")
    assert run_spec == {"key": "value"}


def test_delete_run_spec() -> None:
    profile_store.save_run_spec("default", {"key": "value"})
    profile_store.delete_run_spec("default")
    run_spec = profile_store.load_run_spec("default")
    assert run_spec == {}


def test_ensure_run_spec() -> None:
    assert profile_store.ensure_run_spec("default") is True
    assert profile_store.ensure_run_spec("default") is False


# --------------------------------------------------
# Config
# --------------------------------------------------


def test_load_config() -> None:
    config = profile_store.load_config("default")
    assert config == {}


def test_save_config() -> None:
    profile_store.save_config("default", {"module1": {"key": "value"}})
    config = profile_store.load_config("default")
    assert config == {"module1": {"key": "value"}}


def test_delete_config() -> None:
    profile_store.save_config("default", {"module1": {"key": "value"}})
    profile_store.delete_config("default")
    config = profile_store.load_config("default")
    assert config == {}


def test_ensure_config() -> None:
    assert profile_store.ensure_config("default") is True
    assert profile_store.ensure_config("default") is False


# --------------------------------------------------
# Private Methods
# --------------------------------------------------


def test_load_data() -> None:
    data = profile_store._load_data()
    assert len(data.profiles) == 1

    cached_data = profile_store._load_data()  # cache test
    assert data is cached_data

    profile_store.set_profile(Profile(name="dev"))
    data = profile_store._load_data()
    assert len(data.profiles) == 2


def test_save_data() -> None:
    profile_store._save_data(profile_store._Data())


def test_validate_run_spec() -> None:
    assert profile_store._validate_run_spec(None) == {}
    assert profile_store._validate_run_spec([1]) == {}
    assert profile_store._validate_run_spec({"key": "value"}) == {"key": "value"}


def test_validate_config() -> None:
    assert profile_store._validate_config(None) == {}
    assert profile_store._validate_config([1]) == {}
    assert profile_store._validate_config({"module": {"key": "value"}}) == {
        "module": {"key": "value"}
    }
