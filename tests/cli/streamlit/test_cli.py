from click.testing import CliRunner

from kiari.cli.streamlit import cli as streamlit_cli_module
from kiari.cli.streamlit.cli import streamlit


def test_streamlit_cli_builds_run_options(monkeypatch) -> None:
    captured = {}
    monkeypatch.setattr(
        streamlit_cli_module,
        "run_streamlit",
        lambda profile_name, run_options: captured.update(
            profile_name=profile_name, run_options=run_options
        ),
    )
    result = CliRunner().invoke(
        streamlit,
        [
            "--streamlit-host",
            "localhost",
            "--streamlit-port",
            "9001",
            "--streamlit-layout",
            "centered",
            "--streamlit-authenticator",
            "oidc?provider=google",
        ],
    )
    assert result.exit_code == 0, result.output
    assert captured["run_options"].streamlit_port == 9001
    assert captured["run_options"].streamlit_layout == "centered"
    assert captured["run_options"].streamlit_authenticator == "oidc?provider=google"
