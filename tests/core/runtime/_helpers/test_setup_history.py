from kiarina.agi.history import History

from kiari.core.profile import RunOptions
from kiari.core.runtime import setup_history
from kiari.lib.history_repository import history_repository_registry


async def test_stateless(run_context, text_file_path) -> None:
    history = await setup_history(
        RunOptions(
            no_load=True,
            events=["Hello"],
            file_infos=[text_file_path],
            tool_infos=["hello"],
            tools=["wait"],
        ),
        run_context,
    )

    assert len(history.events) == 1
    assert len(history.file_infos) == 1
    assert len(history.tool_infos) == 2


async def test_load_nonexistent(run_context, text_file_path) -> None:
    history = await setup_history(
        RunOptions(
            events=["Hello"],
            file_infos=[text_file_path],
            tool_infos=["hello"],
            tools=["wait"],
        ),
        run_context,
    )

    assert len(history.events) == 1
    assert len(history.file_infos) == 1
    assert len(history.tool_infos) == 2


async def test_load_existing(run_context, text_file_path) -> None:
    await history_repository_registry.create("in_memory").save(
        History(),
        run_context,
    )

    history = await setup_history(
        RunOptions(
            history_repository="in_memory",
            events=["Hello"],
            file_infos=[text_file_path],
            tool_infos=["hello"],
            tools=["wait"],
        ),
        run_context,
    )

    assert len(history.events) == 0
    assert len(history.file_infos) == 0
    assert len(history.tool_infos) == 1
