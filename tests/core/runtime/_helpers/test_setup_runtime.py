import pytest

from kiari.core.profile import RunOptions
from kiari.core.runtime import setup_runtime


@pytest.fixture(autouse=True)
def cleanup_settings_manager():
    from kiarina.agi import (
        chat_logger,
        cost_logger,
        cost_recorder,
        request_logger,
        tool_logger,
    )

    yield

    cost_recorder.settings_manager.cli_args = {}
    cost_logger.settings_manager.cli_args = {}
    request_logger.settings_manager.cli_args = {}
    chat_logger.settings_manager.cli_args = {}
    tool_logger.settings_manager.cli_args = {}


# TODO: global config と profile config を fixture で生成する


@pytest.fixture(autouse=True)
def setup_i18n_catalogs(tmp_path):
    (tmp_path / "en.yaml").write_text("")
    (tmp_path / "ja.yaml").write_text("")


async def test_setup_runtime(tmp_path) -> None:
    from kiarina.agi.tool import tool_registry

    run_options = RunOptions(
        github_ignore_cache=True,
        github_trusted_usernames=["kiarina"],
        github_skip_trust_verification=True,
        i18n_catalogs=[str(tmp_path)],
        config_vars=["kiari.core.github?ignore_cache=true"],
        node_id="node-123",
    )

    await setup_runtime("default", run_options)

    image_generate = tool_registry.resolve("image_generate")
    assert image_generate.name == "image_generate"

    chrome = tool_registry.resolve("chrome")
    assert chrome.name == "chrome"

    video_predict = tool_registry.resolve("video_predict")
    assert video_predict.name == "video_predict"

    web = tool_registry.resolve("web")
    assert web.name == "web"
