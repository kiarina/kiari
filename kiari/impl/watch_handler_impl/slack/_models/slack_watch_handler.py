import logging
from typing import Any

from kiarina.agi.cost_recorder import cost_recorder_registry
from kiarina.agi.event import AIMessageEvent, Event, ToolMessageEvent
from kiarina.agi.event_builder import build_event
from kiarina.agi.file import get_file_blob
from kiarina.agi.file_info import FileInfo
from kiarina.agi.run_context import RunContext
from pydantic import TypeAdapter
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.web.async_client import AsyncWebClient

from kiari.cli.watch.watch_handler import BaseWatchHandler, WatchSession
from kiari.core.file_info_source import resolve_file_info_specifiers
from kiari.core.runtime import create_agi_options, setup_history
from kiari.impl.watcher_impl.slack import SlackWatchEvent
from kiari.lib.watcher import WatchEvent

from .._settings import SlackWatchHandlerSettings
from .._utils.convert_markdown_to_mrkdwn import convert_markdown_to_mrkdwn
from .._utils.get_bot_token import get_bot_token

logger = logging.getLogger(__name__)


class SlackWatchHandler(BaseWatchHandler):
    def __init__(
        self,
        *args: Any,
        settings: SlackWatchHandlerSettings | None = None,
        **kwargs: Any,
    ) -> None:
        settings_kwargs = {
            key: kwargs.pop(key)
            for key in list(kwargs)
            if key in SlackWatchHandlerSettings.model_fields
        }
        super().__init__(*args, **kwargs)
        base_settings = settings or SlackWatchHandlerSettings()
        self.settings: SlackWatchHandlerSettings = SlackWatchHandlerSettings.model_validate(
            {**base_settings.model_dump(), **settings_kwargs}
        )
        self._installation_store: FileInstallationStore | None = None

    @property
    def installation_store(self) -> FileInstallationStore | None:
        if not self.settings.is_multi_workspace:
            return None

        if self._installation_store is None:
            if self.settings.file_installation_store_base_dir:
                self._installation_store = FileInstallationStore(
                    base_dir=self.settings.file_installation_store_base_dir
                )
            else:
                self._installation_store = FileInstallationStore()

        return self._installation_store

    async def _on_agent_event(self, session: WatchSession, event: Event) -> None:
        try:
            if isinstance(event, AIMessageEvent):
                await self._send_ai_message(session, event)
            elif isinstance(event, ToolMessageEvent):
                await self._send_tool_message(session, event)

        except Exception as e:
            logger.error(f"Error sending message to Slack: {e}", exc_info=True)

    async def _on_event_error(self, session: WatchSession, error: Exception) -> None:
        try:
            team_id, channel_id, thread_ts = self._get_slack_destination(session.watch_event)
            client = await self._create_client(team_id)
            error_text = f"Error occurred:\n```\n{error!s}\n```"

            await client.chat_postMessage(
                channel=channel_id,
                text=error_text,
                thread_ts=thread_ts if thread_ts else None,
            )

        except Exception as e:
            logger.error(f"Error sending error message to Slack: {e}", exc_info=True)

    async def _create_session(self, watch_event: WatchEvent) -> WatchSession:
        run_context = self._create_run_context(watch_event)
        history = await setup_history(self.run_options, run_context)
        text = _get_watch_event_text(watch_event)

        if text or watch_event.attachments:
            history.add_event(
                await build_event(
                    {
                        "text": text,
                        "files": await resolve_file_info_specifiers(watch_event.attachments),
                    },
                    run_context=run_context,
                )
            )

        return WatchSession(
            watch_event=watch_event,
            history=history,
            **create_agi_options(self.run_options),
            cost_recorder=cost_recorder_registry.resolve(),
            run_context=run_context,
        )

    def _create_run_context(self, watch_event: WatchEvent) -> RunContext:
        if isinstance(watch_event, SlackWatchEvent):
            channel_id = watch_event.channel_id or "unknown"
            thread_ts = watch_event.thread_ts or "main"

            return RunContext(
                organization_id=watch_event.team_id or "unknown",
                user_id=channel_id,
                agent_id=f"{channel_id}-{thread_ts}",
            )

        if watch_event.watcher_name == "slack":
            metadata = watch_event.metadata
            channel_id = metadata.get("channel_id") or "unknown"
            thread_ts = metadata.get("thread_ts") or "main"

            return RunContext(
                organization_id=metadata.get("team_id") or "unknown",
                user_id=channel_id,
                agent_id=f"{channel_id}-{thread_ts}",
            )

        return super()._create_run_context(watch_event)

    def _get_slack_destination(self, watch_event: WatchEvent) -> tuple[str | None, str, str]:
        if isinstance(watch_event, SlackWatchEvent):
            team_id = watch_event.team_id or None
            channel_id = watch_event.channel_id
            thread_ts = watch_event.thread_ts
        elif watch_event.watcher_name == "slack":
            team_id = watch_event.metadata.get("team_id")
            channel_id = watch_event.metadata.get("channel_id", "")
            thread_ts = watch_event.metadata.get("thread_ts", "")
        else:
            team_id = self.settings.team_id or None
            channel_id = self.settings.channel_id
            thread_ts = self.settings.thread_ts

        return team_id, channel_id, thread_ts

    async def _create_client(self, team_id: str | None) -> AsyncWebClient:
        bot_token = await get_bot_token(
            self.settings,
            team_id,
            self.installation_store,
        )
        return AsyncWebClient(token=bot_token)

    async def _send_ai_message(
        self,
        session: WatchSession,
        event: AIMessageEvent,
    ) -> None:
        if event.message.tool_calls:
            return

        text = event.message.to_text()

        if not text:
            return

        await self._send_text(session.watch_event, text)

    async def _send_tool_message(
        self,
        session: WatchSession,
        event: ToolMessageEvent,
    ) -> None:
        text = event.message.to_text()

        if text:
            await self._send_text(session.watch_event, text)

        file_infos = _get_tool_message_files(event)

        for file_info in file_infos:
            await self._send_file(session, file_info)

    async def _send_text(self, watch_event: WatchEvent, text: str) -> None:
        team_id, channel_id, thread_ts = self._get_slack_destination(watch_event)
        client = await self._create_client(team_id)

        mrkdwn = convert_markdown_to_mrkdwn(text)

        for part in self._split_text(mrkdwn, 2900):
            await client.chat_postMessage(
                channel=channel_id,
                text=part,
                thread_ts=thread_ts if thread_ts else None,
            )

    async def _send_file(self, session: WatchSession, file_info: FileInfo) -> None:
        team_id, channel_id, thread_ts = self._get_slack_destination(session.watch_event)
        client = await self._create_client(team_id)
        file_blob = await get_file_blob(
            file_info.uri_or_file_path,
            run_context=session.run_context,
        )

        if not file_blob:
            logger.warning(f"File not found: {file_info.uri_or_file_path}")
            return

        await client.files_upload_v2(
            file=file_blob.raw_data,
            filename=file_blob.file_path.split("/")[-1],
            title=file_info.name or file_blob.file_path.split("/")[-1],
            channel=channel_id,
            thread_ts=thread_ts if thread_ts else None,
        )

    def _split_text(self, text: str, max_length: int) -> list[str]:
        if len(text) <= max_length:
            return [text]

        parts: list[str] = []
        current = ""

        for line in text.split("\n"):
            if len(current) + len(line) + 1 > max_length:
                if current:
                    parts.append(current)
                current = line
            else:
                if current:
                    current += "\n" + line
                else:
                    current = line

        if current:
            parts.append(current)

        return parts


def _get_tool_message_files(event: ToolMessageEvent) -> list[FileInfo]:
    file_infos = event.message.artifact.get("file_infos", [])

    if file_infos:
        adapter: TypeAdapter[FileInfo] = TypeAdapter(FileInfo)
        return [adapter.validate_python(file_info) for file_info in file_infos]

    return event.message.get_file_infos()


def _get_watch_event_text(watch_event: WatchEvent) -> str:
    if isinstance(watch_event, SlackWatchEvent):
        return watch_event.message_text

    return watch_event.text
