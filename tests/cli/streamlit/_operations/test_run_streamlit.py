import os
import stat
from pathlib import Path

from kiari.cli.streamlit._operations import run_streamlit as run_streamlit_module
from kiari.cli.streamlit._operations.run_streamlit import run_streamlit
from kiari.core.profile import RunOptions
from kiari.streamlit import StreamlitStartupOptions
from kiari.streamlit._constants import STREAMLIT_STARTUP_FILE_ENV_VAR


def test_run_streamlit_handoff(monkeypatch) -> None:
    captured = {}
    monkeypatch.delenv(STREAMLIT_STARTUP_FILE_ENV_VAR, raising=False)

    def fake_run(command, *, env, check) -> None:
        startup_file = Path(env[STREAMLIT_STARTUP_FILE_ENV_VAR])
        captured["command"] = command
        captured["check"] = check
        captured["mode"] = stat.S_IMODE(startup_file.stat().st_mode)
        captured["startup"] = StreamlitStartupOptions.model_validate_json(startup_file.read_text())

    monkeypatch.setattr(run_streamlit_module.subprocess, "run", fake_run)
    run_streamlit(
        "test",
        RunOptions(
            chat_model="mock",
            streamlit_host="localhost",
            streamlit_port=9000,
            streamlit_headless=True,
        ),
    )

    assert captured["check"] is True
    assert captured["mode"] == 0o600
    assert captured["startup"].profile_name == "test"
    assert captured["startup"].run_options.chat_model == "mock"
    assert captured["command"][-6:] == [
        "--server.address",
        "localhost",
        "--server.port",
        "9000",
        "--server.headless",
        "true",
    ]
    assert STREAMLIT_STARTUP_FILE_ENV_VAR not in os.environ
