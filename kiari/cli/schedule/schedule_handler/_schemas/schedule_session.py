from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from kiarina.agi.agent import AgentOptions
from kiarina.agi.chat_model import ChatOptions
from kiarina.agi.cost_recorder import CostRecorder
from kiarina.agi.event import Event
from kiarina.agi.history import History
from kiarina.agi.prompt import PromptOptions
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import ToolOptions
from kiarina.agi.workflow import WorkflowOptions

from kiari.lib.watcher import WatchEvent

from ...scheduler import Scheduler, ScheduleType


@dataclass
class ScheduleSession:
    history: History
    chat_options: ChatOptions | None
    prompt_options: PromptOptions | None
    workflow_options: WorkflowOptions | None
    tool_options: ToolOptions | None
    agent_options: AgentOptions | None
    cost_recorder: CostRecorder
    run_context: RunContext

    scheduler: Scheduler
    scheduled_time: datetime
    actual_time: datetime
    is_asap: bool = False
    watch_events: list[WatchEvent] = field(default_factory=list)
    last_event: Event | None = None

    @property
    def schedule_type(self) -> ScheduleType:
        return self.scheduler.schedule_type

    @property
    def zone_info(self) -> ZoneInfo:
        return ZoneInfo(self.run_context.time_zone)

    def mark_asap(self) -> None:
        self.is_asap = True

    def add_watch_event(self, event: WatchEvent) -> None:
        self.watch_events.append(event)

    def clear_watch_events(self, events: Iterable[WatchEvent] | None = None) -> None:
        if events is None:
            self.watch_events.clear()
            return

        event_ids = {id(event) for event in events}
        self.watch_events = [event for event in self.watch_events if id(event) not in event_ids]

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
        }
