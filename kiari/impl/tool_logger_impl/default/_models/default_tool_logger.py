import json

from kiarina.agi.console_utils import divider, section_header
from kiarina.agi.message import ToolCall, ToolMessage
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool_logger_impl.console import ConsoleToolLogger
from rich.console import Group, RenderableType
from rich.text import Text

from kiari.core.rich import console_registry, render_message


class DefaultToolLogger(ConsoleToolLogger):
    def log_tool_start(self, tool_call: ToolCall, run_context: RunContext) -> None:
        console_registry.get().print(self._render_tool_start(tool_call, run_context))

    def log_tool_end(self, tool_message: ToolMessage, run_context: RunContext) -> None:
        console_registry.get().print(self._render_tool_end(tool_message, run_context))

    def _render_tool_start(
        self,
        tool_call: ToolCall,
        run_context: RunContext,
    ) -> RenderableType:
        title = f"TOOL CALL: {tool_call}"

        renderables: list[RenderableType] = [
            Text(),
            Text(),
            Text(section_header(title), style="cyan"),
            Text(self._format_run_context(run_context), style="cyan"),
            Text(divider(), style="cyan"),
            Text(),
        ]

        if tool_call.args:
            renderables.extend(
                [
                    Text(
                        json.dumps(tool_call.args, indent=2, ensure_ascii=False),
                        style="cyan",
                    ),
                    Text(),
                ]
            )

        return Group(*renderables)

    def _render_tool_end(
        self,
        tool_message: ToolMessage,
        run_context: RunContext,
    ) -> RenderableType:
        renderables: list[RenderableType] = [
            Text(),
            render_message(tool_message),
        ]

        return Group(*renderables)

    def _format_run_context(self, run_context: RunContext) -> str:
        metadata = run_context.metadata.copy()

        lines: list[str] = []

        # profile
        if profile := metadata.pop("profile", None):
            lines.append(f"profile ({profile}):")
        else:
            lines.append("profile:")

        lines.extend(
            [
                f"  organization_id: {run_context.organization_id}",
                f"          user_id: {run_context.user_id}",
                f"         agent_id: {run_context.agent_id}",
                f"          node_id: {run_context.node_id}",
                f"        time_zone: {run_context.time_zone}",
                f"         language: {run_context.language}",
                f"         currency: {run_context.currency}",
            ]
        )

        # flow
        if loop := metadata.pop("loop", None):
            lines.append(f"flow ({loop}):")
        else:
            lines.append("flow:")

        if history_repository := metadata.pop("history_repository", None):
            lines.append(f"  - {history_repository}")

        if agent := metadata.pop("agent", None):
            lines.append(f"  - {agent}")

        if tool := metadata.pop("tool", None):
            lines.append(f"  - {tool}")

        # remaining metadata
        for key, value in metadata.items():
            if value:
                lines.append(f"{key}: {value}")

        return "\n".join(lines)
