import asyncio
import logging
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock
from urllib.parse import parse_qs, urlsplit

from aiohttp import web
from kiarina.utils.app import user_directory
from pytest import LogCaptureFixture

from kiari.impl.watcher_impl.slack import SlackWatcher, SlackWatcherSettings


async def test_save_attachment(tmp_path: Path) -> None:
    watcher = SlackWatcher(SlackWatcherSettings(attachment_dir=str(tmp_path)))

    source = await watcher._save_attachment("hello world.txt", b"hello")
    split = urlsplit(source)

    assert Path(split.path).read_bytes() == b"hello"
    assert parse_qs(split.query) == {"display_name": ["hello world.txt"]}
    assert Path(split.path).name.endswith("-hello_world.txt")


def test_get_default_attachment_dir() -> None:
    watcher = SlackWatcher(SlackWatcherSettings())

    assert (
        watcher._get_attachment_dir() == user_directory.get_user_cache_dir() / "watcher" / "slack"
    )


async def test_oauth_server_logs_do_not_include_listen_address(
    caplog: LogCaptureFixture, unused_tcp_port: int
) -> None:
    host = "127.0.0.1"
    watcher = SlackWatcher(
        SlackWatcherSettings(
            is_multi_workspace=True,
            oauth_server_host=host,
            oauth_server_port=unused_tcp_port,
        )
    )
    watcher._app = cast(
        Any, SimpleNamespace(server=lambda **_: SimpleNamespace(web_app=web.Application()))
    )
    stop_event = asyncio.Event()
    stop_event.set()

    with caplog.at_level(logging.INFO):
        await watcher._start_oauth_server(stop_event)

    assert "OAuth server started" in caplog.text
    assert host not in caplog.text
    assert str(unused_tcp_port) not in caplog.text


async def test_watch_starting_log_does_not_include_listen_address(
    caplog: LogCaptureFixture, unused_tcp_port: int
) -> None:
    host = "127.0.0.1"
    watcher = SlackWatcher(
        SlackWatcherSettings(
            is_multi_workspace=True,
            oauth_server_host=host,
            oauth_server_port=unused_tcp_port,
        )
    )
    watcher._handler = cast(
        Any,
        SimpleNamespace(start_async=AsyncMock(), close_async=AsyncMock()),
    )
    watcher._app = cast(
        Any, SimpleNamespace(server=lambda **_: SimpleNamespace(web_app=web.Application()))
    )
    stop_event = asyncio.Event()
    stop_event.set()

    with caplog.at_level(logging.INFO):
        assert [event async for event in watcher.watch(stop_event)] == []

    assert "OAuth server starting" in caplog.text
    assert host not in caplog.text
    assert str(unused_tcp_port) not in caplog.text
