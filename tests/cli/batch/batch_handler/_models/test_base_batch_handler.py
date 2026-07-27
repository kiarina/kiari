import pytest
from kiarina.agi.event import AIMessageEvent

from kiari.cli.batch.batch_handler import BaseBatchHandler, BatchRequest
from kiari.core.profile import RunOptions


class ExampleBatchHandler(BaseBatchHandler):
    pass


def test_base_batch_handler() -> None:
    handler = ExampleBatchHandler("test_profile", RunOptions())
    handler.name = "example"

    print(f"name: {handler.name}")
    print(f"history_repository: {handler.history_repository}")

    assert True


async def test_handle_request(text_file_path, setup_run_context) -> None:
    handler = ExampleBatchHandler("test_profile", RunOptions())

    request = BatchRequest(
        text="hello",
        attachments=[text_file_path],
    )

    async with handler.handle_request(request) as session:
        await handler.on_agent_event(session, AIMessageEvent.create("hello"))

    with pytest.raises(Exception, match="Test error"):
        async with handler.handle_request(request) as session:
            raise Exception("Test error")

    assert True
