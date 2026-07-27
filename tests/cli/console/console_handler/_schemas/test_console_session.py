from kiari.cli.console.console_handler import (
    ConsoleSession,
)


async def test_clear_buffer(
    session: ConsoleSession,
) -> None:
    session.text = "hello"
    session.attachments = ["README.md"]
    session.max_iterations = 3
    session.until_end = True
    session.until_tool_calls = ["temp_call"]
    session.until_tool_runs = ["temp_run"]

    session.clear_buffer()

    assert session.text == ""
    assert session.attachments == []
    assert session.max_iterations is None
    assert session.until_end is None
    assert session.until_tool_calls is None
    assert session.until_tool_runs is None


def test_as_run_agent_kwargs(session: ConsoleSession) -> None:
    session.agent_options = {
        "max_iterations": 7,
        "until_end": False,
        "until_tool_calls": ["base_call"],
        "until_tool_runs": ["base_run"],
    }

    session.max_iterations = 3
    session.until_end = True
    session.until_tool_calls = ["temp_call"]
    session.until_tool_runs = ["temp_run"]

    kwargs = session.as_run_agent_kwargs()

    assert kwargs["agent_options"] == {
        "max_iterations": 3,
        "until_end": True,
        "until_tool_calls": ["temp_call"],
        "until_tool_runs": ["temp_run"],
    }

    assert session.agent_options == {
        "max_iterations": 7,
        "until_end": False,
        "until_tool_calls": ["base_call"],
        "until_tool_runs": ["base_run"],
    }
