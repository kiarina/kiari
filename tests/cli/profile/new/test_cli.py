import pytest

from kiari.cli.profile.new.cli import _new
from kiari.core.profile import profile_store


@pytest.fixture(autouse=True)
def cleanup_profiles():
    yield
    profile_store.delete_all()


def test_new() -> None:
    _new("dev", description="hello")
    assert profile_store.has_profile("dev")

    with pytest.raises(Exception, match="Profile already exists"):
        _new("dev")
