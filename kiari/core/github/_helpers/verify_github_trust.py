import logging

import questionary
from kiarina.i18n import get_i18n, get_system_language

from kiari.core.rich import console_registry, join_renderables, render_status_block
from kiari.core.terminal import create_prompt_toolkit_io, has_interactive_tty

from .._i18n import GitHubI18n
from .._models.github_path_spec import GitHubPathSpec
from .._services.github_trusted_source_store import github_trusted_source_store
from .._settings import settings_manager
from .._types.github_path_pattern import GitHubPathPattern

type IsTrustedSource = bool

logger = logging.getLogger(__name__)


async def verify_github_trust(
    github_path: GitHubPathPattern | GitHubPathSpec,
) -> IsTrustedSource:
    t = get_i18n(GitHubI18n, get_system_language())
    console = console_registry.get()
    settings = settings_manager.get_settings()

    if isinstance(github_path, str):
        spec = GitHubPathSpec.from_string(github_path)
    else:
        spec = github_path

    if settings.skip_trust_verification:
        logger.info("GitHub trust verification skipped by settings.")
        return True

    if spec.username in settings.trusted_usernames:
        logger.info(f"User '{spec.username}' is trusted by settings.")
        return True

    trusted = await github_trusted_source_store.load()

    if spec.username in trusted:
        logger.info(f"User '{spec.username}' is already trusted.")
        return True

    security_warning_source = t.security_warning_source.format(
        username=spec.username,
        repo=spec.repo,
        file_path=spec.file_path,
    )

    console.print(
        render_status_block(
            title=t.security_warning_title,
            lines=[
                t.security_warning_intro,
                "",
                f"  [yellow]{security_warning_source}[/yellow]",
                f"  [blue]{t.security_warning_url.format(url=spec.blob_view_url)}[/blue]",
                "",
                f"[red]{t.security_warning_access}[/red]",
                f"[red]{t.security_warning_trust}[/red]",
            ],
            status="error",
        )
    )

    choice = await _ask_trust_prompt(spec.username)

    if choice == "no" or choice is None:
        console.print(
            join_renderables(
                [
                    "",
                    f"[yellow]{t.execution_cancelled}[/yellow]",
                    "",
                ],
                markup=True,
            )
        )
        return False

    if choice == "always":
        trusted.append(spec.username)
        await github_trusted_source_store.save(trusted)

        console.print(
            join_renderables(
                [
                    "",
                    f"[green]{t.added_to_trusted.format(username=spec.username)}[/green]",
                    "",
                ],
                markup=True,
            )
        )

    return True


async def _ask_trust_prompt(username: str) -> str | None:
    t = get_i18n(GitHubI18n, get_system_language())

    if not has_interactive_tty():
        logger.warning("GitHub trust confirmation requires a TTY.")
        console_registry.get().print(t.trust_prompt_requires_tty, style="yellow")
        return None

    choice = await questionary.select(
        t.trust_prompt,
        choices=[
            questionary.Choice(title=t.trust_choice_yes, value="yes"),
            questionary.Choice(
                title=t.trust_choice_always.format(username=username),
                value="always",
            ),
            questionary.Choice(title=t.trust_choice_no, value="no"),
        ],
        **create_prompt_toolkit_io(),
    ).ask_async()

    if choice is None or isinstance(choice, str):
        return choice
    raise TypeError("GitHub trust prompt returned an invalid choice")
