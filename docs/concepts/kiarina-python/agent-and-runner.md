# Agent and Runner (kiarina-agi-runner)

This package provides the agent execution engine. Every kiari execution mode—batch,
console, watch, and schedule—eventually delegates to it. See
[Execution Modes](../execution-modes.md) for mode-specific behavior.

See [Documented Versions](overview.md#documented-versions) for the assumed versions.

## kiarina.agi.agent

This module contains the core agent runtime.

- Execution helpers: `run_agent()`, which returns an asynchronous iterator of events,
  plus `invoke_agent()` and `stream_agent()`
- `run_agent(history, *, run_context, chat_options, prompt_options, workflow_options,
  tool_options, agent_options, cost_recorder, stop_event, ...)`: runs the agent loop over
  a `History` and emits `Event` objects
- Implementations extend `BaseAgent` and register with `agent_registry`
- `AgentSettings` and `settings_manager` configure defaults, presets, and custom
  implementations; see the [common component pattern](overview.md#common-pattern-registry--settings--implementation)
- `AgentContext` carries runtime state into implementations
- `MissingToolsError` reports requested tools that cannot be resolved

The standard implementation is under
`packages/kiarina-agi-runner/src/kiarina/agi/agent_impl/vanilla/`.

kiari calls the runtime from:

- `kiari/cli/batch/_operations/run_batch.py`
- `kiari/cli/console/_operations/run_console.py`
- `kiari/cli/watch/_operations/run_watch.py`
- `kiari/cli/schedule/_operations/run_schedule.py`

## kiarina.agi.task_runner

`run_task()`, `invoke_task()`, and `stream_task()` run agent work as tasks. Tests live
under `packages/kiarina-agi-runner/tests/task_runner/`.

## kiarina.agi.structured_output

These helpers request structured LLM results:

- `generate_dict()`: generate a dictionary
- `generate_model()`: generate a Pydantic model
- `select_option()`: select from a fixed set of options

Tests live under `packages/kiarina-agi-runner/tests/structured_output/`.
