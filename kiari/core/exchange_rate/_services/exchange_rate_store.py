import logging
import time
from pathlib import Path

from kiarina.currency import CurrencyCode, ExchangeRateNotFoundError, get_exchange_rate
from kiarina.utils.app import user_directory
from kiarina.utils.file.asyncio import read_json_dict, write_json_dict

from .._exceptions.exchange_rate_not_loaded_error import ExchangeRateNotLoadedError

logger = logging.getLogger(__name__)

_TTL = 24 * 60 * 60


class ExchangeRateStore:
    def __init__(self) -> None:
        self._rates: dict[CurrencyCode, float] = {}

    @property
    def _file_path(self) -> Path:
        return user_directory.get_user_cache_dir() / "exchange_rates.json"

    async def load(self, currency: CurrencyCode) -> None:
        if currency in self._rates:
            return

        cache_data = await read_json_dict(self._file_path, default={})
        now = time.time()

        if cache_item := cache_data.get(currency):
            if isinstance(cache_item, dict):
                rate = cache_item.get("rate")
                timestamp = cache_item.get("timestamp")

                if isinstance(rate, (int, float)) and isinstance(timestamp, (int, float)):
                    if now - timestamp < _TTL:
                        self._rates[currency] = float(rate)
                        return

        try:
            rate = await get_exchange_rate(from_currency="USD", to_currency=currency)
            logger.info(f"Fetched exchange rate for {currency}: {rate}")

        except ExchangeRateNotFoundError:
            logger.warning(f"Exchange rate not found for currency: {currency}")
            return

        cache_data[currency] = {"rate": rate, "timestamp": now}
        await write_json_dict(self._file_path, cache_data)
        self._rates[currency] = rate

    def get(self, currency: CurrencyCode) -> float:
        if currency not in self._rates:
            raise ExchangeRateNotLoadedError(
                f"Exchange rate for {currency!r} is not loaded. Call load() first."
            )

        return self._rates[currency]


exchange_rate_store = ExchangeRateStore()
