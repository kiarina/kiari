import kiarina.lib.slack
from slack_sdk.oauth.installation_store import FileInstallationStore

from .._settings import SlackWatchHandlerSettings


async def get_bot_token(
    settings: SlackWatchHandlerSettings,
    team_id: str | None,
    installation_store: FileInstallationStore | None = None,
) -> str:
    if settings.is_multi_workspace:
        if not installation_store:
            raise ValueError("installation_store is required for multi-workspace mode")

        if not team_id:
            raise ValueError("team_id is required for multi-workspace mode")

        bot = await installation_store.async_find_bot(
            enterprise_id=None,
            team_id=team_id,
        )

        if bot is None:
            raise ValueError(f"Bot not found in installation_store for team: {team_id}")

        return bot.bot_token

    slack_settings = kiarina.lib.slack.settings_manager.get_settings(settings.slack_settings_key)

    if not slack_settings.bot_token:
        raise ValueError("Slack Bot Token is not configured")

    return slack_settings.bot_token.get_secret_value()
