from kiarina.agi.history import History

from kiari.impl.history_repository_impl.local import (
    create_local_history_repository,
)


async def test_local_history_repository(tmp_path, run_context) -> None:
    repository = create_local_history_repository(file_name="test.json")

    await repository.delete(run_context)
    assert await repository.load(run_context) is None

    await repository.save(History(metadata={"value": "saved"}), run_context)
    loaded = await repository.load(run_context)
    assert loaded is not None
    assert loaded.metadata == {"value": "saved"}
