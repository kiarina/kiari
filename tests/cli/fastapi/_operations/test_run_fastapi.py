import os
import stat
from pathlib import Path

from kiari.cli.fastapi._operations import run_fastapi as run_fastapi_module
from kiari.cli.fastapi._operations.run_fastapi import run_fastapi
from kiari.core.profile import RunOptions
from kiari.fastapi import FastAPIStartupOptions
from kiari.fastapi._constants import FASTAPI_STARTUP_FILE_ENV_VAR


def test_run_fastapi_handoff_and_reload(monkeypatch) -> None:
    captured = {}
    monkeypatch.delenv(FASTAPI_STARTUP_FILE_ENV_VAR, raising=False)

    def fake_run(app, **kwargs) -> None:
        startup_file = Path(os.environ[FASTAPI_STARTUP_FILE_ENV_VAR])
        captured["app"] = app
        captured["kwargs"] = kwargs
        captured["mode"] = stat.S_IMODE(startup_file.stat().st_mode)
        captured["startup"] = FastAPIStartupOptions.model_validate_json(startup_file.read_text())

    monkeypatch.setattr(run_fastapi_module.uvicorn, "run", fake_run)

    run_fastapi(
        "test",
        RunOptions(chat_model="mock", fastapi_port=9000),
    )

    assert captured["app"] == "kiari.fastapi.app:create_app"
    assert captured["kwargs"]["factory"] is True
    assert captured["kwargs"]["reload"] is True
    assert captured["kwargs"]["workers"] is None
    assert captured["mode"] == 0o600
    assert captured["startup"].profile_name == "test"
    assert captured["startup"].run_options.chat_model == "mock"
    assert FASTAPI_STARTUP_FILE_ENV_VAR not in os.environ


def test_run_fastapi_workers_disable_reload(monkeypatch) -> None:
    captured = {}
    monkeypatch.setenv(FASTAPI_STARTUP_FILE_ENV_VAR, "previous")
    monkeypatch.setattr(
        run_fastapi_module.uvicorn,
        "run",
        lambda app, **kwargs: captured.update(kwargs),
    )

    run_fastapi("test", RunOptions(fastapi_workers=3))

    assert captured["workers"] == 3
    assert captured["reload"] is False
    assert os.environ[FASTAPI_STARTUP_FILE_ENV_VAR] == "previous"
