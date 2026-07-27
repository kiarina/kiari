from typing import Any

from kiarina.agi.agent import AgentOptions
from kiarina.agi.chat_model import ChatOptions
from kiarina.agi.prompt import PromptOptions
from kiarina.agi.tool import ToolOptions
from kiarina.agi.workflow import WorkflowOptions

from kiari.core.profile import RunOptions


def create_agi_options(run_options: RunOptions) -> dict[str, Any]:
    return {
        "chat_options": _create_chat_options(run_options),
        "prompt_options": _create_prompt_options(run_options),
        "workflow_options": _create_workflow_options(run_options),
        "tool_options": _create_tool_options(run_options),
        "agent_options": _create_agent_options(run_options),
    }


def _create_agent_options(run_options: RunOptions) -> AgentOptions:
    options = AgentOptions()

    if run_options.agent is not None:
        options["agent"] = run_options.agent
    if run_options.file_limits is not None:
        options["file_limits"] = run_options.file_limits
    if run_options.max_iterations is not None:
        options["max_iterations"] = run_options.max_iterations
    if run_options.until_end is not None:
        options["until_end"] = run_options.until_end
    if run_options.until_tool_calls:
        options["until_tool_calls"] = run_options.until_tool_calls
    if run_options.until_tool_runs:
        options["until_tool_runs"] = run_options.until_tool_runs

    return options


def _create_tool_options(run_options: RunOptions) -> ToolOptions:
    options = ToolOptions()

    if run_options.tools:
        options["tools"] = run_options.tools
    if run_options.pre_hooks:
        options["pre_hooks"] = run_options.pre_hooks
    if run_options.post_hooks:
        options["post_hooks"] = run_options.post_hooks

    return options


def _create_workflow_options(run_options: RunOptions) -> WorkflowOptions:
    options = WorkflowOptions()

    if run_options.workflow is not None:
        options["workflow"] = run_options.workflow

    return options


def _create_prompt_options(run_options: RunOptions) -> PromptOptions:
    options = PromptOptions()

    if run_options.prompt is not None:
        options["prompt"] = run_options.prompt
    if run_options.prompt_limits is not None:
        options["limits"] = run_options.prompt_limits

    if run_options.system_messages:
        if options.get("prompt"):
            raise ValueError("Cannot specify system_messages when prompt is specified")

        from kiarina.agi.prompt import prompt_registry

        options["prompt"] = prompt_registry.resolve(
            "structured", system_texts=run_options.system_messages
        )

    return options


def _create_chat_options(run_options: RunOptions) -> ChatOptions:
    chat_options = ChatOptions()

    if run_options.chat_model is not None:
        chat_options["chat_model"] = run_options.chat_model
    if run_options.tool_choice is not None:
        chat_options["tool_choice"] = run_options.tool_choice
    if run_options.parallel_tool_calls is not None:
        chat_options["parallel_tool_calls"] = run_options.parallel_tool_calls
    if run_options.streaming is not None:
        chat_options["streaming"] = run_options.streaming

    return chat_options
