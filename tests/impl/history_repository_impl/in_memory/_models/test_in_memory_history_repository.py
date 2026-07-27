from kiarina.agi.history import History

from kiari.impl.history_repository_impl.in_memory import InMemoryHistoryRepository


async def test_in_memory_history_repository(run_context) -> None:
    repository = InMemoryHistoryRepository()
    history = History(metadata={"value": "saved"})

    await repository.save(history, run_context)
    history.metadata["value"] = "mutated"

    loaded = await repository.load(run_context)
    assert loaded is not None
    assert loaded.metadata == {"value": "saved"}

    await repository.delete(run_context)
    assert await repository.load(run_context) is None
