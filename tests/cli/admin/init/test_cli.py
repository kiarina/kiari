import pytest
from rich.console import Console

from kiari.cli.admin.init.cli import _init


@pytest.fixture(autouse=True)
def cleanup_config_file():
    from kiari.core.paths import get_config_file_path
    from kiari.core.profile import profile_store

    yield
    get_config_file_path().unlink(missing_ok=True)
    profile_store.delete_all()


def test_init(console: Console) -> None:
    _init()

    output = console.export_text()
    assert "Initialization completed." in output
