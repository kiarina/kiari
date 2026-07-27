from kiarina.agi.message import HumanMessage
from kiarina.agi.tool_info import ToolInfo
from rich.console import Console

from kiari.cli.console.console_handler import (
    ConsoleSession,
)
from kiari.cli.console.console_renderer import render_console_status
from kiari.core.profile import RunOptions


def test_specified(
    console: Console,
    run_options: RunOptions,
    session: ConsoleSession,
) -> None:
    # session
    session.history.add_message(HumanMessage.create("hello"))
    session.history.metadata["foo"] = "bar"
    session.history.add_tool_info(
        ToolInfo(
            name="search",
            description="Search files.",
        )
    )
    session.history.add_tool_info(
        ToolInfo(
            name="browser",
            description="Use browser.",
            state="inactive",
        )
    )
    session.history.add_tool_info(
        ToolInfo(
            name="shell",
            description="Run shell command.",
            state="disabled",
        )
    )
    session.attachments.append("README.md")
    session.chat_options = {
        "chat_model": "session_mock",
        "tool_choice": "auto",
    }
    session.tool_options = {
        "tools": ["session_search"],
    }
    session.tts_enabled = True
    session.stt_enabled = True
    session.agent_options = {
        "max_iterations": 7,
        "until_end": False,
        "until_tool_calls": ["session_call"],
        "until_tool_runs": ["session_run"],
    }

    # run_options
    run_options.chat_model = "mock"
    run_options.no_load = True
    run_options.no_save = True
    run_options.tts_model = "mock"
    run_options.audio_source = "queue"
    run_options.vad_model = "mock"
    run_options.asr_model = "mock"
    run_options.tool_choice = "auto"
    run_options.tools = ["search"]
    run_options.pre_hooks = ["approval?message=Proceed@search,browser"]
    run_options.post_hooks = ["summarize?verbose=true@search"]
    run_options.until_tool_calls = ["search"]
    run_options.until_tool_runs = ["search"]

    console.print(
        render_console_status(
            session,
            profile_name="default",
            run_options=run_options,
        ),
    )

    output = console.export_text()

    assert "       App:" in output
    assert "   Console:" in output
    assert "RunContext:" in output
    assert "      Flow:" in output
    assert "   History:" in output
    assert "     Input:" in output
    assert "    Output:" in output
    assert "      Tool:" in output
    assert "      Hook:" in output
    assert " Condition:" in output
    assert "org=" in output
    assert "user=" in output
    assert "agent=" in output
    assert "node=" in output
    assert "tz=" in output
    assert "lang=" in output
    assert "currency=" in output
    assert "Flow:" in output
    assert "profile=default" in output
    assert "run_spec=profile" in output
    assert "config=global,profile" in output
    assert "Console:" in output
    assert "tts=yes" in output
    assert "tts_model=mock" in output
    assert "stt=yes" in output
    assert "audio_source=queue" in output
    assert "vad_model=mock" in output
    assert "asr_model=mock" in output
    assert "History:" in output
    assert "history_repository=null" in output
    assert "no_load=yes" in output
    assert "no_save=yes" in output
    assert "agent=vanilla" in output
    assert "workflow=vanilla" in output
    assert "prompt=vanilla" in output
    assert "chat_model=session_mock" in output
    assert "tool_choice=auto" in output
    assert "Input:" in output
    assert "messages=1" in output
    assert "custom_events=0" in output
    assert "file_infos=0+1" in output
    assert "pending_tool_calls=0" in output
    assert "metadata=1" in output
    assert "Output:" in output
    assert "tool_choice=auto" in output
    assert "tool_infos=active:search,inactive:browser,disabled:shell" in output
    assert "Tool:" in output
    assert "tools=session_search" in output
    assert "Hook:" in output
    assert "pre_hooks=approval@search,browser" in output
    assert "post_hooks=summarize@search" in output
    assert "Condition:" in output
    assert "max_iterations=7" in output
    assert "until_end=no" in output
    assert "until_tool_calls=session_call" in output
    assert "until_tool_runs=session_run" in output


def test_empty(
    console: Console,
    run_options: RunOptions,
    session: ConsoleSession,
) -> None:
    console.print(
        render_console_status(
            session,
            profile_name="default",
            run_options=run_options,
        ),
    )

    output = console.export_text()

    assert "max_iterations=60" in output
    assert "until_end=no" in output
    assert "until_tool_calls=-" in output
    assert "until_tool_runs=-" in output
    assert "Console:" in output
    assert "History:" in output
    assert "history_repository=null" in output
    assert "no_load=no" in output
    assert "no_save=no" in output
    assert "tts=no" in output
    assert "tts_model=openai" in output
    assert "stt=no" in output
    assert "audio_source=mic" in output
    assert "vad_model=local" in output
    assert "asr_model=openai" in output
    assert "agent=vanilla" in output
    assert "workflow=vanilla" in output
    assert "prompt=vanilla" in output
    assert "chat_model=openai" in output
    assert "tools=-" in output
    assert "metadata=0" in output
