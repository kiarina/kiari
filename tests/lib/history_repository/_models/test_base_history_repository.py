from kiarina.agi.history import History

from kiari.lib.history_repository import BaseHistoryRepository


class ExampleHistoryRepository(BaseHistoryRepository):
    pass


async def test_base_history_repository(run_context) -> None:
    repository = ExampleHistoryRepository()
    repository.name = "example"

    print(f"name: {repository.name}")
    print(f"__str__: {repository}")

    assert (await repository.load(run_context)) is None
    await repository.save(History(), run_context)
    await repository.delete(run_context)
