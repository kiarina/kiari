# Workflow and Prompt (kiarina-agi-flow)

This package defines the workflow, prompt, section, and state layers within one agent
iteration. The [agent](agent-and-runner.md) owns the loop, a workflow owns the steps inside
the loop, a prompt owns one LLM call, and sections compose the prompt body.

See [Documented Versions](overview.md#documented-versions) for the assumed versions.

## kiarina.agi.workflow

A workflow is one unit of processing flow.

- Define one with `@workflow`, or extend `BaseWorkflow` and register it with
  `workflow_registry`
- Run one with `run_workflow()`, `invoke_workflow()`, or `stream_workflow()`
- Configure defaults, presets, and custom implementations through `WorkflowSettings`,
  `settings_manager`, and specifiers

See the [common component pattern](overview.md#common-pattern-registry--settings--implementation).
The standard implementation is under
`packages/kiarina-agi-flow/src/kiarina/agi/workflow_impl/vanilla/`.

## kiarina.agi.prompt

A prompt represents one LLM call. Its API mirrors workflows:
`@prompt`, `BasePrompt`, `run_prompt()`, `invoke_prompt()`, `stream_prompt()`,
`prompt_registry`, and `PromptSettings`.

Standard implementations are under
`packages/kiarina-agi-flow/src/kiarina/agi/prompt_impl/`, including `vanilla/` and
`structured/`. Tests are under `tests/prompt/` and `tests/prompt_impl/`.

Use `rg 'kiarina.agi.prompt' kiari/` to find kiari call sites.

## kiarina.agi.section / section_container

Sections compose a prompt body.

- `BaseSection` and `SectionContext` define section behavior
- `Weight` assigns priority
- `SectionContainer` combines sections into the final body

Implementations and tests are under `section_impl/`, `tests/section/`, and
`tests/section_container/`.

## kiarina.agi.state / state_machine

States model transitions within a flow.

- Define states with `@state`, or with `BaseState` and `StateContext`
- `StateMachine` drives transitions

Implementations and tests are under `state_impl/`, `tests/state/`, and
`tests/state_machine/`.
