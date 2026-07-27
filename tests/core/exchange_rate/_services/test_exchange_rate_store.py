import time

import pytest

from kiari.core.exchange_rate._exceptions.exchange_rate_not_loaded_error import (
    ExchangeRateNotLoadedError,
)
from kiari.core.exchange_rate._services.exchange_rate_store import ExchangeRateStore


@pytest.fixture(autouse=True)
def setup(tmp_path):
    from kiarina.utils.app import settings_manager

    settings_manager.cli_args = {"user_cache_dir": str(tmp_path)}
    yield
    settings_manager.cli_args = {}


@pytest.fixture
def store() -> ExchangeRateStore:
    return ExchangeRateStore()


@pytest.fixture
def mock_fetch(monkeypatch: pytest.MonkeyPatch):
    def _set(side_effect):
        import kiari.core.exchange_rate._services.exchange_rate_store as _module

        async def _fake(**kwargs):
            if isinstance(side_effect, Exception):
                raise side_effect

            return side_effect

        monkeypatch.setattr(_module, "get_exchange_rate", _fake)

    return _set


# --- get ---


def test_get_raises_before_load(store: ExchangeRateStore) -> None:
    with pytest.raises(ExchangeRateNotLoadedError):
        store.get("JPY")


# --- load + get ---


async def test_load_and_get(store: ExchangeRateStore, mock_fetch) -> None:
    mock_fetch(150.0)
    await store.load("JPY")
    assert store.get("JPY") == 150.0


async def test_load_is_idempotent(store: ExchangeRateStore, mock_fetch) -> None:
    mock_fetch(150.0)
    await store.load("JPY")

    mock_fetch(999.0)  # API が違う値を返すようにする
    await store.load("JPY")  # 2回目はスキップされる
    assert store.get("JPY") == 150.0


async def test_load_does_not_load_when_not_found(store: ExchangeRateStore, mock_fetch) -> None:
    from kiarina.currency import ExchangeRateNotFoundError

    mock_fetch(ExchangeRateNotFoundError("JPY"))
    await store.load("JPY")

    with pytest.raises(ExchangeRateNotLoadedError):
        store.get("JPY")


# --- file cache ---


async def test_load_uses_file_cache(mock_fetch, tmp_path) -> None:
    mock_fetch(150.0)
    store1 = ExchangeRateStore()
    await store1.load("JPY")

    mock_fetch(999.0)  # API が違う値を返すようにする
    store2 = ExchangeRateStore()  # オンメモリは空
    await store2.load("JPY")  # ファイルキャッシュから取得する
    assert store2.get("JPY") == 150.0


async def test_load_ignores_expired_file_cache(
    store: ExchangeRateStore, mock_fetch, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_fetch(150.0)
    future = time.time() + 24 * 60 * 60 + 1
    monkeypatch.setattr(time, "time", lambda: future)
    await store.load("JPY")  # キャッシュは期限切れ → API fetch される

    assert store.get("JPY") == 150.0
