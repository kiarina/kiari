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
from kiarina.agi.workflow import WorkflowOptions

from kiari.core.profile import RunOptions

from .request_body import RequestBody


@dataclass
class FastAPISession:
    request_body: RequestBody
    request_headers: dict[str, str]
    run_options: RunOptions
    history: History
    chat_options: ChatOptions | None
    prompt_options: PromptOptions | None
    workflow_options: WorkflowOptions | None
    tool_options: ToolOptions | None
    agent_options: AgentOptions | None
    cost_recorder: CostRecorder
    run_context: RunContext
    run_kwargs: dict[str, Any] = field(default_factory=dict)
    last_event: Event | None = None
    error: Exception | None = None

    def as_run_agent_kwargs(self) -> dict[str, Any]:
        return {
            "history": self.history,
            "chat_options": self.chat_options,
            "prompt_options": self.prompt_options,
            "workflow_options": self.workflow_options,
            "tool_options": self.tool_options,
            "agent_options": self.agent_options,
            "cost_recorder": self.cost_recorder,
            "run_context": self.run_context,
            **self.run_kwargs,
        }
