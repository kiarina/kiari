import asyncio
import logging
from collections.abc import AsyncIterator

from google.cloud.pubsub import SubscriberClient  # type: ignore
from kiarina.lib.google import get_credentials

from kiari.lib.watcher import BaseWatcher

from .._schemas.pubsub_watch_event import PubsubWatchEvent
from .._settings import PubsubWatcherSettings

logger = logging.getLogger(__name__)


class PubsubWatcher(BaseWatcher):
    def __init__(self, settings: PubsubWatcherSettings) -> None:
        super().__init__()
        self.settings: PubsubWatcherSettings = settings
        self._subscriber: SubscriberClient | None = None

    @property
    def subscriber(self) -> SubscriberClient:
        if self._subscriber is None:
            credentials = get_credentials(self.settings.google_auth_settings_key)
            self._subscriber = SubscriberClient(credentials=credentials)

        return self._subscriber

    async def watch(self, stop_event: asyncio.Event) -> AsyncIterator[PubsubWatchEvent]:
        subscription_path = self.subscriber.subscription_path(
            self.settings.project_id,
            self.settings.subscription_id,
        )

        logger.info(f"Connected to subscription: {subscription_path}")

        while not stop_event.is_set():
            try:
                pull_task = asyncio.create_task(
                    asyncio.to_thread(
                        self.subscriber.pull,
                        request={
                            "subscription": subscription_path,
                            "max_messages": self.settings.max_messages,
                        },
                        timeout=self.settings.timeout,
                    )
                )

                stop_task = asyncio.create_task(stop_event.wait())
                await asyncio.wait(
                    [pull_task, stop_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )
                stop_task.cancel()

                if stop_event.is_set():
                    pull_task.cancel()

                    try:
                        await pull_task
                    except asyncio.CancelledError:
                        pass

                    break

                response = await pull_task

                if response.received_messages:
                    ack_ids = [msg.ack_id for msg in response.received_messages]
                    await asyncio.to_thread(
                        self.subscriber.acknowledge,
                        request={
                            "subscription": subscription_path,
                            "ack_ids": ack_ids,
                        },
                    )

                for received_message in response.received_messages:
                    try:
                        message = received_message.message
                        yield PubsubWatchEvent.create(
                            watcher_name=self.name,
                            data=message.data.decode("utf-8"),
                            message_id=message.message_id,
                            publish_time=str(message.publish_time),
                            attributes=dict(message.attributes),
                        )

                    except Exception as e:
                        logger.error(
                            f"Error processing message {received_message.message.message_id}: {e}",
                            exc_info=True,
                        )

            except Exception as e:
                logger.error(f"Error receiving message: {e}", exc_info=True)
                await asyncio.sleep(5)
