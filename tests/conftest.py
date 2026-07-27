import logging
import os
import re
from pathlib import Path

import pytest
from kiarina.agi.file_info import FileInfo
from kiarina.agi.run_context import RunContext
from rich.console import Console


def pytest_addoption(parser) -> None:
    parser.addoption("--chat-provider", default=[], action="append")
    parser.addoption("--chat-model", default=[], action="append")
    parser.addoption("--run-costly", action="store_true", default=False)


@pytest.fixture(autouse=True)
def skip_costly(request: pytest.FixtureRequest) -> None:
    if request.node.get_closest_marker("costly"):
        if not os.path.exists(
            Path(__file__).resolve().parent.parent / ".costly"
        ) and not request.config.getoption("--run-costly"):
            pytest.skip("Skipping costly test. Use --run-costly to run it.")


@pytest.fixture(scope="session", autouse=True)
def configure_app() -> None:
    from contextlib import suppress

    from kiarina.utils.app import AppAlreadyConfiguredError, configure

    with suppress(AppAlreadyConfiguredError):
        configure(app_author="kiarina", app_name="kiari_tests")


@pytest.fixture(scope="session", autouse=True)
def setup_logger() -> None:
    for name in ["kiari"]:
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)


@pytest.fixture(scope="session", autouse=True)
def setup_github_settings() -> None:
    from kiari.core.github import settings_manager

    settings_manager.user_config = {"trusted_usernames": ["kiarina"]}


@pytest.fixture
def console():
    from kiari.core.rich import console_registry

    console = Console(record=True, width=1000)
    console_registry.register("default", console)
    yield console
    console_registry.clear()


# --------------------------------------------------
# Directory
# --------------------------------------------------


@pytest.fixture
def run_context(request: pytest.FixtureRequest) -> RunContext:
    return RunContext(
        organization_id="kiari",
        user_id=request.module.__name__,
        agent_id=re.sub(r"[^a-zA-Z0-9_-]", "", request.node.name),
        node_id="pytest",
    )


@pytest.fixture(autouse=True)
def setup_run_context(run_context: RunContext) -> None:
    from kiarina.agi.run_context import settings_manager

    settings_manager.set_cli_args("organization_id", run_context.organization_id)
    settings_manager.set_cli_args("user_id", run_context.user_id)
    settings_manager.set_cli_args("agent_id", run_context.agent_id)
    settings_manager.set_cli_args("node_id", run_context.node_id)


@pytest.fixture
def test_assets_dir() -> Path:
    return Path(__file__).parent / "assets"


@pytest.fixture
def resource_data_dir():
    return Path(__file__).parent.parent / "kiari" / "resources"


# --------------------------------------------------
# File Path
# --------------------------------------------------


@pytest.fixture
def text_file_path(test_assets_dir: Path) -> str:
    return str(test_assets_dir / "txt" / "hello_world_11b.txt")


@pytest.fixture
def image_file_path(test_assets_dir: Path) -> str:
    return str(test_assets_dir / "png" / "miineko_256x256_799b.png")


@pytest.fixture
def audio_file_path(test_assets_dir: Path) -> str:
    return str(test_assets_dir / "mp3" / "tone_2s_16kb.mp3")


@pytest.fixture
def pdf_file_path(test_assets_dir: Path) -> str:
    return str(test_assets_dir / "pdf" / "text_only_portrait_1p_17kb.pdf")


@pytest.fixture
def video_file_path(test_assets_dir: Path) -> str:
    return str(test_assets_dir / "mp4" / "shape_animation_1600x900_24fps_13s_4400kb.mp4")


# --------------------------------------------------
# File Info
# --------------------------------------------------


@pytest.fixture
async def text_file_info(text_file_path, run_context) -> FileInfo:
    from kiarina.agi.file_info_loader import load_file_info

    file_info = await load_file_info(text_file_path, run_context=run_context)
    assert file_info is not None
    return file_info


@pytest.fixture
async def image_file_info(image_file_path, run_context) -> FileInfo:
    from kiarina.agi.file_info_loader import load_file_info

    file_info = await load_file_info(image_file_path, run_context=run_context)
    assert file_info is not None
    return file_info
