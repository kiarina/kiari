from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest
from kiarina.utils.file import read_yaml_dict
from pydantic_settings_manager import clear_user_configs, load_user_configs


@pytest.fixture(autouse=True)
def setup_settings() -> Iterator[None]:
    settings_path = Path(__file__).resolve().parent / "test_settings.yaml"

    if not settings_path.is_file():
        pytest.skip(f"test_settings.yaml does not exist: {settings_path}")

    user_configs = read_yaml_dict(settings_path)

    if not user_configs:
        pytest.skip(f"test_settings.yaml is empty: {settings_path}")

    load_user_configs(user_configs)
    yield
    clear_user_configs(user_configs)


@pytest.fixture(autouse=True)
def check_health(setup_settings: None) -> None:
    from kiari.impl.web_impl.kiapi import settings_manager

    url = f"{settings_manager.settings.kiapi_base_url}/health"

    try:
        response = httpx.get(url, timeout=5.0)
    except httpx.RequestError as error:
        pytest.skip(f"kiapi is not reachable: {url} ({error})")

    if response.status_code != 200:
        pytest.skip(f"kiapi is not healthy: {url} (status code: {response.status_code})")
