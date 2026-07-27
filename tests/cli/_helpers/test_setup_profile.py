import pytest

from kiari.cli import setup_profile
from kiari.core.profile import profile_store


@pytest.fixture(autouse=True)
def clean_profile_store():
    yield
    profile_store.delete_all()


def test_not_save() -> None:
    profile_name, run_spec, run_options = setup_profile(
        profile_name=None,
        save_mode=None,
        run_spec={},
    )

    assert profile_name == "default"
    assert run_spec == {}
    print(f"run_options: {run_options.model_dump_json(indent=2)}")


def test_reset() -> None:
    profile_name, run_spec, run_options = setup_profile(
        profile_name=None,
        save_mode="reset",
        run_spec={},
    )

    assert profile_name == "default"
    assert run_spec == {}
    print(f"run_options: {run_options.model_dump_json(indent=2)}")
