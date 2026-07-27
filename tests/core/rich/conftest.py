import pytest
from rich.console import Console


@pytest.fixture
def console() -> Console:
    return Console(record=True, width=1000)
