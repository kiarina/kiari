import pytest

from kiari.cli.batch._operations.run_batch import run_batch
from kiari.cli.batch.batch_handler import BatchRequest
from kiari.core.profile import RunOptions


async def test_run_batch(capsys: pytest.CaptureFixture) -> None:
    await run_batch(
        "default",
        RunOptions(output_text=True, chat_model="mock"),
        BatchRequest(text="hello"),
    )

    captured = capsys.readouterr()
    assert "hello" in captured.out
