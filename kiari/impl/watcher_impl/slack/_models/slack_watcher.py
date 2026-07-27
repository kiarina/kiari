import asyncio
import logging
import re
from collections.abc import AsyncIterator, Awaitable, Callable, Coroutine
from pathlib import Path
from typing import Any, Literal, cast
from urllib.parse import urlencode
from uuid import uuid4

import aiofiles
import aiohttp
import kiarina.lib.slack
from kiarina.utils.app import user_directory
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.async_app import AsyncApp
from slack_bolt.oauth.async_oauth_settings import AsyncOAuthSettings
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.web.async_client import AsyncWebClient

from kiari.lib.watcher import BaseWatcher

from .._schemas.slack_watch_event import SlackWatchEvent
from .._settings import SlackWatcherSettings

logger = logging.getLogger(__name__)

type TeamID = str
type UserID = str
type ChannelID = str
type ChannelType = Literal["im", "mpim", "channel", "group"]


class SlackWatcher(BaseWatcher):
    def __init__(self, settings: SlackWatcherSettings) -> None:
        super().__init__()
        self.settings: SlackWatcherSettings = settings
        self._app: AsyncApp | None = None
        self._handler: AsyncSocketModeHandler | None = None
        self._queue: asyncio.Queue[SlackWatchEvent] | None = None
        self._bot_user_id_cache: dict[TeamID, UserID] = {}
        self._channel_type_cache: dict[ChannelID, ChannelType] = {}

    @property
    def slack_settings(self) -> kiarina.lib.slack.SlackSettings:
        return kiarina.lib.slack.settings_manager.get_settings(self.settings.slack_settings_key)

    @property
    def app_token(self) -> str:
        if not self.slack_settings.app_token:
            raise ValueError("Slack App Token is not configured")

        return self.slack_settings.app_token.get_secret_value()

    @property
    def bot_token(self) -> str:
        if not self.slack_settings.bot_token:
            raise ValueError("Slack Bot Token is not configured")

        return self.slack_settings.bot_token.get_secret_value()

    @property
    def file_installation_store(self) -> FileInstallationStore:
        if not self.settings.file_installation_store_base_dir:
            return FileInstallationStore()

        return FileInstallationStore(base_dir=self.settings.file_installation_store_base_dir)

    @property
    def app(self) -> AsyncApp:
        if self._app is None:
            if self.settings.is_multi_workspace:
                self._app = AsyncApp(
                    signing_secret=self.slack_settings.signing_secret.get_secret_value(),
                    oauth_settings=AsyncOAuthSettings(
                        client_id=self.slack_settings.client_id,
                        client_secret=self.slack_settings.client_secret.get_secret_value(),
                        scopes=self.slack_settings.scopes,
                        installation_store=self.file_installation_store,
                    ),
                    installation_store=self.file_installation_store,
                )
            else:
                self._app = AsyncApp(token=self.bot_token)

            self._app.event("message")(self._handle_message)
            self._app.event("app_mention")(self._ignore_app_mention)

        return self._app

    @property
    def handler(self) -> AsyncSocketModeHandler:
        if self._handler is None:
            self._handler = AsyncSocketModeHandler(self.app, self.app_token)

        return self._handler

    async def watch(self, stop_event: asyncio.Event) -> AsyncIterator[SlackWatchEvent]:
        self._queue = asyncio.Queue()
        oauth_server_task: asyncio.Task[None] | None = None

        logger.info("Connected to Slack workspace")

        if self.settings.is_multi_workspace:
            oauth_server_task = asyncio.create_task(self._start_oauth_server(stop_event))
            logger.info(
                f"OAuth server starting at "
                f"http://{self.settings.oauth_server_host}:"
                f"{self.settings.oauth_server_port}"
            )

        start_handler = cast(
            Callable[[], Coroutine[Any, Any, None]],
            self.handler.start_async,
        )
        handler_task: asyncio.Task[None] = asyncio.create_task(start_handler())

        try:
            while not stop_event.is_set():
                try:
                    yield await asyncio.wait_for(self._queue.get(), timeout=1.0)

                except TimeoutError:
                    continue

        finally:
            close_handler = cast(Callable[[], Awaitable[None]], self.handler.close_async)
            await close_handler()
            await self._cancel_task(handler_task)

            if oauth_server_task:
                await self._cancel_task(oauth_server_task)

    async def _handle_message(
        self, event: dict[str, Any], say: Any, client: AsyncWebClient
    ) -> None:
        try:
            if event.get("bot_id"):
                return

            subtype = event.get("subtype")
            if subtype in ("message_changed", "message_deleted", "channel_join"):
                return

            channel = event.get("channel", "")
            team_id = event.get("team", "")

            if self.settings.channel_ids and channel not in self.settings.channel_ids:
                return

            bot_user_id = await self._get_bot_user_id(client, team_id)

            if self.settings.require_mention_in_channels:
                channel_type = await self._get_channel_type(client, channel)

                if channel_type not in ("im", "mpim"):
                    text = event.get("text", "")
                    if not self._is_bot_mentioned(text, bot_user_id):
                        return

            text = event.get("text", "")
            user = event.get("user", "")
            ts = event.get("ts", "")
            thread_ts = event.get("thread_ts")
            team = event.get("team", "")

            attachments = []
            if event.get("files"):
                attachments = await self._download_files(client, event["files"])

            watch_event = SlackWatchEvent.create(
                watcher_name=self.name,
                team_id=team,
                channel_id=channel,
                user_id=user,
                ts=ts,
                text=text,
                thread_ts=thread_ts or "",
                attachments=attachments,
            )

            if self._queue:
                await self._queue.put(watch_event)

            logger.debug(f"Message received from Slack: {channel}")

        except Exception as e:
            logger.error(f"Error processing Slack event: {e}", exc_info=True)

    async def _ignore_app_mention(self, event: dict[str, Any], say: Any) -> None:
        pass

    async def _get_bot_user_id(self, client: AsyncWebClient, team_id: TeamID) -> UserID:
        if team_id not in self._bot_user_id_cache:
            response = await client.auth_test()
            self._bot_user_id_cache[team_id] = str(response["user_id"])

        return self._bot_user_id_cache[team_id]

    def _is_bot_mentioned(self, text: str, bot_user_id: UserID) -> bool:
        return f"<@{bot_user_id}>" in text

    async def _get_channel_type(self, client: AsyncWebClient, channel_id: ChannelID) -> ChannelType:
        if channel_id not in self._channel_type_cache:
            try:
                response = await client.conversations_info(channel=channel_id)

                if response["ok"]:
                    channel = response["channel"]
                    assert isinstance(channel, dict)

                    if channel.get("is_im"):
                        self._channel_type_cache[channel_id] = "im"
                    elif channel.get("is_mpim"):
                        self._channel_type_cache[channel_id] = "mpim"
                    elif channel.get("is_group"):
                        self._channel_type_cache[channel_id] = "group"
                    else:
                        self._channel_type_cache[channel_id] = "channel"
                else:
                    self._channel_type_cache[channel_id] = "channel"

            except Exception as e:
                logger.warning(f"Failed to get channel type for {channel_id}: {e}")
                self._channel_type_cache[channel_id] = "channel"

        return self._channel_type_cache[channel_id]

    async def _download_files(
        self, client: AsyncWebClient, files: list[dict[str, Any]]
    ) -> list[str]:
        attachments: list[str] = []

        for file_data in files:
            try:
                file_size_mb = file_data.get("size", 0) / (1024 * 1024)

                if file_size_mb > self.settings.max_file_size_mb:
                    logger.warning(
                        f"File too large to download: {file_size_mb:.2f}MB "
                        f"(max: {self.settings.max_file_size_mb}MB)"
                    )
                    continue

                url_private = file_data.get("url_private")
                if not url_private:
                    continue

                async with aiohttp.ClientSession() as session:
                    headers = {"Authorization": f"Bearer {client.token}"}
                    async with session.get(url_private, headers=headers) as resp:
                        if resp.status != 200:
                            logger.error(f"Failed to download file: HTTP {resp.status}")
                            continue

                        file_content = await resp.read()

                file_name = file_data.get("name", "slack_file")
                attachments.append(await self._save_attachment(file_name, file_content))

            except Exception as e:
                logger.error(f"Error downloading file: {e}", exc_info=True)

        return attachments

    async def _save_attachment(self, file_name: str, file_content: bytes) -> str:
        attachment_dir = self._get_attachment_dir()
        attachment_dir.mkdir(parents=True, exist_ok=True)

        safe_file_name = _sanitize_file_name(file_name)
        file_path = attachment_dir / f"{uuid4().hex}-{safe_file_name}"

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_content)

        return f"{file_path}?{urlencode({'display_name': file_name})}"

    def _get_attachment_dir(self) -> Path:
        if self.settings.attachment_dir:
            return Path(self.settings.attachment_dir)

        return user_directory.get_user_cache_dir() / "watcher" / "slack"

    async def _start_oauth_server(self, stop_event: asyncio.Event) -> None:
        from aiohttp import web

        runner: web.AppRunner | None = None

        try:
            server = self.app.server(
                port=self.settings.oauth_server_port,
                path="/slack/events",
                host=self.settings.oauth_server_host,
            )

            runner = web.AppRunner(server.web_app)
            await runner.setup()

            site = web.TCPSite(
                runner,
                host=self.settings.oauth_server_host,
                port=self.settings.oauth_server_port,
            )
            await site.start()

            logger.info(
                f"OAuth server started at "
                f"http://{self.settings.oauth_server_host}:"
                f"{self.settings.oauth_server_port}"
            )

            await stop_event.wait()

        except asyncio.CancelledError:
            logger.info("OAuth server stopping...")
            raise

        except Exception as e:
            logger.error(f"OAuth server error: {e}", exc_info=True)
            raise

        finally:
            if runner:
                await runner.cleanup()
                logger.info("OAuth server stopped")

    async def _cancel_task(self, task: asyncio.Task[Any]) -> None:
        if task.done():
            return

        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass


def _sanitize_file_name(file_name: str) -> str:
    safe_file_name = re.sub(r"[^A-Za-z0-9._-]+", "_", file_name).strip("._")
    return safe_file_name or "slack_file"
