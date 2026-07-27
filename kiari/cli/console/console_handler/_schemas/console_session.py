from dataclasses import dataclass, field
from typing import Any

from kiarina.agi.agent import AgentOptions
from kiarina.agi.chat_model import ChatOptions
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.event import Event
from kiarina.agi.history import History
from kiarina.agi.prompt import PromptOptions
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import ToolOptions
from kiarina.agi.tool_info import ToolName
from kiarina.agi.workflow import WorkflowOptions

from kiari.core.file_info_source import FileInfoSource


@dataclass
class ConsoleSession:
    history: History
    chat_options: ChatOptions
    prompt_options: PromptOptions
    workflow_options: WorkflowOptions
    tool_options: ToolOptions
    agent_options: AgentOptions
    cost_recorder: CostRecorder
    run_context: RunContext

    text: str = ""
    attachments: list[FileInfoSource] = field(default_factory=list)
    max_iterations: int | None = None
    until_end: bool | None = None
    until_tool_calls: list[ToolName] | None = None
    until_tool_runs: list[ToolName] | None = None

    last_event: Event | None = None
    tts_enabled: bool = False
    stt_enabled: bool = False

    def clear_buffer(self) -> None:
        self.text = ""
        self.attachments = []
        self.max_iterations = None
        self.until_end = None
        self.until_tool_calls = None
        self.until_tool_runs = None

    def as_run_agent_kwargs(self) -> dict[str, Any]:
        agent_options = AgentOptions(**self.agent_options)

        if self.max_iterations is not None:
            agent_options["max_iterations"] = self.max_iterations
        if self.until_end is not None:
            agent_options["until_end"] = self.until_end
        if self.until_tool_calls is not None:
            agent_options["until_tool_calls"] = self.until_tool_calls
        if self.until_tool_runs is not None:
            agent_options["until_tool_runs"] = self.until_tool_runs

        return {
            "history": self.history,
            "chat_options": self.chat_options,
            "prompt_options": self.prompt_options,
            "workflow_options": self.workflow_options,
            "tool_options": self.tool_options,
            "agent_options": agent_options,
            "cost_recorder": self.cost_recorder,
            "run_context": self.run_context,
        }
