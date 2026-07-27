from pathlib import Path

import pytest

from kiari.core.profile import RunOptions
from kiari.fastapi import FastAPIStartupOptions
from kiari.fastapi._constants import FASTAPI_STARTUP_FILE_ENV_VAR
from kiari.fastapi._helpers.load_fastapi_startup_options import (
    load_fastapi_startup_options,
)


def test_load_fastapi_startup_options(monkeypatch, tmp_path: Path) -> None:
    startup_file = tmp_path / "startup.json"
    startup_file.write_text(
        FastAPIStartupOptions(
            profile_name="test",
            run_options=RunOptions(chat_model="mock"),
        ).model_dump_json()
    )
    monkeypatch.setenv(FASTAPI_STARTUP_FILE_ENV_VAR, str(startup_file))

    startup_options = load_fastapi_startup_options()

    assert startup_options.profile_name == "test"
    assert startup_options.run_options.chat_model == "mock"


def test_load_fastapi_startup_options_errors(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv(FASTAPI_STARTUP_FILE_ENV_VAR, raising=False)
    with pytest.raises(RuntimeError, match="is not set"):
        load_fastapi_startup_options()

    startup_file = tmp_path / "startup.json"
    startup_file.write_text('{"schema_version": 2}')
    monkeypatch.setenv(FASTAPI_STARTUP_FILE_ENV_VAR, str(startup_file))
    with pytest.raises(RuntimeError, match="Invalid FastAPI startup file"):
        load_fastapi_startup_options()
