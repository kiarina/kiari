import pytest

from kiari.cli.profile.set.cli import _set
from kiari.core.profile import profile_store


@pytest.fixture(autouse=True)
def cleanup_profiles():
    yield
    profile_store.delete_all()


def test_set() -> None:
    with pytest.raises(Exception, match="Profile not found"):
        _set("dev")

    with pytest.raises(Exception, match="No updates specified"):
        _set("default")

    _set(description="hello")
