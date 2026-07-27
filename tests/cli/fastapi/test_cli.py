from click.testing import CliRunner

import kiari.cli.fastapi.cli as fastapi_cli
from kiari.cli.fastapi.cli import fastapi


def test_fastapi_cli(monkeypatch) -> None:
    captured = {}

    def fake_run_fastapi(profile_name, run_options) -> None:
        captured["profile_name"] = profile_name
        captured["run_options"] = run_options

    monkeypatch.setattr(fastapi_cli, "run_fastapi", fake_run_fastapi)

    result = CliRunner().invoke(
        fastapi,
        [
            "--profile",
            "test",
            "--chat-model",
            "mock",
            "--fastapi-port",
            "9000",
            "--fastapi-workers",
            "2",
        ],
    )

    assert result.exit_code == 0
    assert captured["profile_name"] == "test"
    assert captured["run_options"].chat_model == "mock"
    assert captured["run_options"].fastapi_port == 9000
    assert captured["run_options"].fastapi_workers == 2
