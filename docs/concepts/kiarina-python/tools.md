# Tools (kiarina-agi-tool)

This package defines agent tools, execution hooks, and tool logging. kiari implements many
tools of its own, so `kiari/impl/tool_impl/` is the best source of concrete examples.

See [Documented Versions](overview.md#documented-versions) for the assumed versions.

## kiarina.agi.tool

- Define a tool with `@tool`, or extend `BaseTool` and register it with
  `tool_registry`
- Execute a tool with `run_tool()`
- Inputs and outputs use `ToolInput` and `ToolOutput`; `ToolOutputLike` values are
  normalized
- `ToolContext` carries runtime state into implementations
- `AdditionalFieldConfig` adds fields to a tool schema
- `ToolError` represents an implementation failure; `ToolNotFoundError` represents
  failed resolution
- `ToolSettings`, `settings_manager`, and `ToolSpecifier` configure resolution
- `PreHookBinding` and `PostHookBinding` attach hooks to tools

See the [common component pattern](overview.md#common-pattern-registry--settings--implementation).
Standard implementations live under
`packages/kiarina-agi-tool/src/kiarina/agi/tool_impl/`.

Examples in `kiari/impl/tool_impl/` include:

- `web/` and `subprocess/`: multi-action tools
- `text_file_view/`, `text_file_edit/`, and media viewers: file tools
- `image_generate/` and `video_predict/`: generation tools
- `gui/` and `change_directory/`: environment tools

See [Tool Implementation Patterns](../tool-implementation-patterns.md) for the single-action
and multi-action structures used by kiari.

## kiarina.agi.pre_hook / post_hook

Hooks run before or after a tool for confirmation, transformation, or recording.

- Define hooks with `@prehook` and `@posthook`, or extend `BasePreHook` and
  `BasePostHook`
- `run_pre_hooks()` and `run_post_hooks()` receive their corresponding context and
  return their corresponding output type
- `PreHookError` and `PostHookError` report hook failures

Implementations live under `pre_hook_impl/` and `post_hook_impl/`.

## kiarina.agi.tool_logger

This module defines the tool logging abstraction. kiari implementations live under
`kiari/impl/tool_logger_impl/`.

## kiarina.agi.langchain_tool

`LangChainTool` adapts a LangChain tool to the kiarina tool contract. Tests live under
`packages/kiarina-agi-tool/tests/langchain_tool/`.
