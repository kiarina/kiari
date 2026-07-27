from collections.abc import Sequence

from kiari.core.profile import ProfileName, RunOptions

from ..extension_command import ExtensionCommandContext, extension_command_registry


async def run_ext(
    profile_name: ProfileName,
    run_options: RunOptions,
    command_name: str,
    args: Sequence[str],
) -> None:
    command = extension_command_registry.resolve(command_name)

    context = ExtensionCommandContext(
        profile_name=profile_name,
        run_options=run_options,
    )

    await command.run(context, args)
