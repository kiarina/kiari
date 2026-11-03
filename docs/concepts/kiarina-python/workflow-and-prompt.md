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
- `Weight` assigns relative token allowances among resizable sections
- `SectionContainer` combines sections into the final body

Implementations and tests are under `section_impl/`, `tests/section/`, and
`tests/section_container/`.

### Resize contract

The current lock includes the Section resize changes introduced in kiarina-python
`4aed3a00`, beyond the published `kiarina-agi-flow` 2.11.0 behavior. Check the git source in
`uv.lock`, not only the package version, when reproducing this behavior.

Subclasses of `BaseSection` implement `async _resize(reduce)`, not `resize`. The public
`resize(reduce)` async iterator calls this hook and clears cached estimates in `finally`,
including on failure, cancellation, or explicit closure. `HistorySection` and
`FileInfoSection` use this hook; `StaticSection` and `ToolSection` remain non-resizable.
kiari currently defines no custom Section classes to migrate.

A resize can advance an internal stage without reducing tokens immediately. The prompt
does not impose a no-progress or resize-count cutoff. A Section must exhaust its finite
resizing stages and return `False` from `is_resizable()` when no further resizing is possible.

Prompt resizing changes the presentation held by sections, not `History`. By contrast,
Agent pre-run file refresh/adjustment may replace entries in the stored file pool, and
kiari's `history_compact` explicitly changes stored events. Persistent compaction is not
automatically triggered by `run_prompt`.

`run_prompt` retains its original `ChatLimits` and derives an effective limit from the
current token conversion factor. Local resize iterations do not multiply previous limits
again. Provider overflow responses still calibrate estimated versus reported token counts;
without a reported count, the current allowance is reduced. Provider retries and local
resizing have separate termination rules.

Both exhausted resize capacity and fixed sections exceeding the budget raise
`TokenOverflowError` to the caller. For a local failure its optional `limit` is the effective
local estimated-token allowance; provider errors may use the provider's token units.
The public `resize(reduce)` call remains unchanged, but custom subclasses that override it
must migrate their implementation to `_resize` to receive cache invalidation.

## kiarina.agi.state / state_machine

States model transitions within a flow.

- Define states with `@state`, or with `BaseState` and `StateContext`
- `StateMachine` drives transitions

Implementations and tests are under `state_impl/`, `tests/state/`, and
`tests/state_machine/`.
