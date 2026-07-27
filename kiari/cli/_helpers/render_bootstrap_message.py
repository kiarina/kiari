from kiarina.agi.console_utils import divider, section_header
from rich.console import Group, RenderableType
from rich.text import Text

from kiari.core.profile import ProfileName, RunOptions, RunSpec


def render_bootstrap_message(
    exec_file: str | None,
    profile_name: ProfileName,
    run_spec: RunSpec,
    run_options: RunOptions,
) -> RenderableType | None:
    if run_options.log_level not in ("DEBUG", "INFO"):
        return None

    style = "black"

    renderables: list[RenderableType] = [
        Text("kiari version 1.0.0", style=style),
    ]

    if exec_file:
        renderables.append(Text(f"+ exec: {exec_file}", style=style))

    renderables.append(Text(f"+ profile: {profile_name}", style=style))
    renderables.append(Text(section_header("RUN OPTIONS"), style=style))

    if run_spec:
        for k, v in run_spec.items():
            renderables.append(Text(f"{k}: {v}", style=style))
    else:
        renderables.append(Text("No run options specified", style=style))

    renderables.append(Text(divider(), style=style))

    return Group(*renderables)
