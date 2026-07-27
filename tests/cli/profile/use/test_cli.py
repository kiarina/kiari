import pytest

from kiari.cli.profile.use.cli import _use
from kiari.core.profile import Profile, profile_store


@pytest.fixture(autouse=True)
def cleanup_profiles():
    yield
    profile_store.delete_all()


def test_use() -> None:
    with pytest.raises(Exception, match="Profile not found: dev"):
        _use("dev")

    profile_store.set_profile(Profile(name="dev"))
    _use("dev")
    assert profile_store.get_current() == "dev"
