from pathlib import Path

import pytest

from kiari.core.profile import RunOptions
from kiari.streamlit import StreamlitStartupOptions
from kiari.streamlit._constants import STREAMLIT_STARTUP_FILE_ENV_VAR
from kiari.streamlit._helpers.load_streamlit_startup_options import (
    load_streamlit_startup_options,
)


def test_load_streamlit_startup_options(monkeypatch, tmp_path: Path) -> None:
    path = tmp_path / "startup.json"
    path.write_text(
        StreamlitStartupOptions(
            profile_name="test", run_options=RunOptions(chat_model="mock")
        ).model_dump_json()
    )
    monkeypatch.setenv(STREAMLIT_STARTUP_FILE_ENV_VAR, str(path))
    result = load_streamlit_startup_options()
    assert result.profile_name == "test"
    assert result.run_options.chat_model == "mock"


def test_load_streamlit_startup_options_requires_file(monkeypatch) -> None:
    monkeypatch.delenv(STREAMLIT_STARTUP_FILE_ENV_VAR, raising=False)
    with pytest.raises(RuntimeError, match="is not set"):
        load_streamlit_startup_options()
