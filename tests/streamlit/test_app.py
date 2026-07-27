from pathlib import Path

from kiarina.utils.app import user_directory
from streamlit.testing.v1 import AppTest

from kiari.core.profile import RunOptions
from kiari.streamlit import StreamlitStartupOptions
from kiari.streamlit._constants import STREAMLIT_STARTUP_FILE_ENV_VAR


def test_app_renders_agent_onboarding(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(user_directory, "get_user_data_dir", lambda: tmp_path / "data")
    monkeypatch.setattr(user_directory, "get_user_cache_dir", lambda: tmp_path / "cache")
    monkeypatch.setattr(user_directory, "get_user_config_dir", lambda: tmp_path / "config")
    startup_file = tmp_path / "startup.json"
    startup_file.write_text(
        StreamlitStartupOptions(
            profile_name="default",
            run_options=RunOptions(
                chat_model="mock",
                cost_recorder="null",
                finalizers=[],
                no_load=True,
                no_save=True,
            ),
        ).model_dump_json()
    )
    monkeypatch.setenv(STREAMLIT_STARTUP_FILE_ENV_VAR, str(startup_file))
    app_path = Path(__file__).parents[2] / "kiari" / "streamlit" / "app.py"
    app = AppTest.from_file(app_path, default_timeout=10).run()
    assert not app.exception
    assert app.title[0].value == "Kiari Chat"
    assert app.info[0].value == "Create or select an agent to start."

    app.text_input[0].set_value("agent-1")
    app.button[0].click().run(timeout=10)
    assert not app.exception
    assert app.selectbox[0].value == "agent-1"
    assert app.chat_input

    app.chat_input[0].set_value("hello").run(timeout=10)
    assert not app.exception
    assert len(app.chat_message) >= 2
