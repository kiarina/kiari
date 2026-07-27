import pytest

from kiari.cli.profile.copy.cli import _copy
from kiari.core.profile import profile_store


@pytest.fixture(autouse=True)
def cleanup_profiles():
    yield
    profile_store.delete_all()


def test_copy() -> None:
    with pytest.raises(Exception, match="Expected"):
        _copy(())

    with pytest.raises(Exception, match="Profile not found"):
        _copy(("dev", "prd"))

    with pytest.raises(Exception, match="Profile already exists"):
        _copy(("default", "default"))

    _copy(("default", "dev"))
    assert profile_store.has_profile("dev")
