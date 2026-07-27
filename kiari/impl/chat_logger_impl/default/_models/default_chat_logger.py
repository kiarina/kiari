import json
import sys
from collections.abc import Iterator
from contextlib import contextmanager

from kiarina.agi.chat_logger_impl.console import ConsoleChatLogger
from kiarina.agi.console_utils import divider, section_header, stderr_color
from kiarina.agi.message import AIMessage, ToolCall
from kiarina.agi.run_context import RunContext
from rich.console import Group, RenderableType
from rich.text import Text

from kiari.core.rich import console_registry


class DefaultChatLogger(ConsoleChatLogger):
    # --------------------------------------------------
    # Public Methods (invoke)
    # --------------------------------------------------

    def log_chat_invoke_start(self, run_context: RunContext) -> None:
        console_registry.get().print(self._render_chat_start(run_context))

    def log_chat_invoke_end(
        self,
        ai_message: AIMessage,
        run_context: RunContext,
    ) -> None:
        console_registry.get().print(self._render_chat_end(run_context, ai_message=ai_message))

    # --------------------------------------------------
    # Public Methods (stream)
    # --------------------------------------------------

    @contextmanager
    def log_chat_stream(self, run_context: RunContext) -> Iterator[None]:
        console = console_registry.get()

        console.print(self._render_chat_start(run_context))
        console.print(self._render_chat_end(run_context))

        with stderr_color("yellow"):
            try:
                yield
            finally:
                print(flush=True, file=sys.stderr)

    def _render_chat_start(self, run_context: RunContext) -> RenderableType:
        title = self._format_ai_call_title(run_context)

        renderables: list[RenderableType] = [
            Text(),
            Text(),
            Text(section_header(title), style="blue"),
            Text(self._format_run_context(run_context), style="blue"),
            Text(divider(), style="blue"),
        ]

        return Group(*renderables)

    # --------------------------------------------------
    # Private Methods
    # --------------------------------------------------

    def _render_chat_end(
        self,
        run_context: RunContext,
        ai_message: AIMessage | None = None,
    ) -> RenderableType:
        title = self._format_ai_message_title(run_context)

        renderables: list[RenderableType] = [
            Text(),
            Text(),
            Text(section_header(title), style="yellow"),
            Text(),
        ]

        if ai_message:
            renderables.append(self._render_ai_message(ai_message))

        return Group(*renderables)

    def _render_ai_message(self, ai_message: AIMessage) -> RenderableType:
        renderables: list[RenderableType] = []

        if contents_text := ai_message.contents_to_text():
            renderables.append(Text(contents_text, style="yellow"))

        for tool_call in ai_message.tool_calls:
            renderables.append(self._render_tool_call(tool_call))

        return Group(*renderables)

    def _render_tool_call(self, tool_call: ToolCall) -> RenderableType:
        renderables: list[RenderableType] = [
            Text(),
            Text(),
            Text(f"[TOOL CALL] {tool_call}", style="yellow"),
        ]

        if tool_call.args:
            renderables.append(
                Text(
                    json.dumps(tool_call.args, indent=2, ensure_ascii=False),
                    style="yellow",
                )
            )

        return Group(*renderables)

    def _format_ai_call_title(self, run_context: RunContext) -> str:
        props: list[str] = []

        if chat_model := run_context.metadata.get("chat_model"):
            props.append(str(chat_model))

        if token_count := run_context.metadata.get("token_count"):
            props.append(f"{token_count} tokens")

        return f"AI CALL: {', '.join(props)}" if props else "AI CALL"

    def _format_ai_message_title(self, run_context: RunContext) -> str:
        props: list[str] = []

        if chat_model := run_context.metadata.get("chat_model"):
            props.append(str(chat_model))

        return f"AI MESSAGE: {', '.join(props)}" if props else "AI MESSAGE"

    def _format_run_context(self, run_context: RunContext) -> str:
        metadata = run_context.metadata.copy()
        metadata.pop("token_count", None)
        metadata.pop("chat_model", None)

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

        if workflow := metadata.pop("workflow", None):
            if state := metadata.pop("state", None):
                lines.append(f"  - {workflow} [{state}]")
                workflow = f"{workflow} [{state}]"
            else:
                lines.append(f"  - {workflow}")

        if prompt := metadata.pop("prompt", None):
            lines.append(f"  - {prompt}")

        if sections := metadata.pop("section_container", None):
            lines.append(f"    - {sections}")

        if chat_provider := metadata.pop("chat_provider", None):
            lines.append(f"  - {chat_provider}")

        # input
        if messages := metadata.pop("messages", None):
            lines.append(f"input: {messages}")

        # output
        output: list[str] = []

        if metadata.pop("tool_choice", None) == "auto":
            output.append("text")

        if tool_infos := metadata.pop("tool_infos", None):
            output.append(f"tool_call({tool_infos})")

        if output:
            lines.append(f"output: {' | '.join(output)}")

        # remaining metadata
        for key, value in metadata.items():
            if value:
                lines.append(f"{key}: {value}")

        return "\n".join(lines)
