import pytest

from kiari.lib.history_repository import (
    BaseHistoryRepository,
    history_repository_registry,
)


@pytest.fixture(autouse=True)
def cleanup():
    yield
    history_repository_registry.clear()


def test_history_repository_registry() -> None:

    class ExampleHistoryRepository(BaseHistoryRepository):
        pass

    history_repository_registry.register("test", ExampleHistoryRepository)

    repository = history_repository_registry.create("test")
    assert isinstance(repository, ExampleHistoryRepository)
    assert repository.name == "test"
