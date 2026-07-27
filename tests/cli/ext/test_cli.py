from click.testing import CliRunner

import kiari.cli.ext.cli as ext_cli
from kiari.cli.ext.cli import ext
from kiari.core.profile import RunOptions


def test_ext(monkeypatch) -> None:
    calls = []

    monkeypatch.setattr(
        ext_cli.cli,
        "setup_profile",
        lambda profile_name, save_mode, run_spec: (
            profile_name or "default",
            run_spec,
            RunOptions.model_validate(run_spec),
        ),
    )
    monkeypatch.setattr(ext_cli.cli, "render_bootstrap_message", lambda *args: None)

    async def fake_setup_runtime(*args, **kwargs) -> None:
        calls.append(("setup_runtime", args, kwargs))

    async def fake_run(*args, **kwargs) -> None:
        calls.append(("run", args, kwargs))

    monkeypatch.setattr(ext_cli, "setup_runtime", fake_setup_runtime)
    monkeypatch.setattr(ext_cli.cli, "run", fake_run)

    result = CliRunner().invoke(
        ext,
        [
            "--profile",
            "test",
            "--chat-model",
            "mock",
            "tts",
            "--instructions",
            "slowly",
            "hello",
        ],
    )

    assert result.exit_code == 0
    assert calls[0][0] == "setup_runtime"
    assert calls[1][0] == "run"

    _, run_args, _ = calls[1]
    assert run_args[3] == "tts"
    assert run_args[4] == ["--instructions", "slowly", "hello"]
