# Tool Implementation Patterns

Built-in tools under `kiari/impl/tool_impl/` use one of two structures:

- a single-action tool that exposes one capability
- a multi-action tool that groups related operations

See [Tools](kiarina-python/tools.md) for the underlying kiarina-agi-tool API.

## Shared Structure

```text
kiari/impl/tool_impl/<tool_name>/
├── __init__.py
├── _i18n.py
├── _models/<tool_name>.py
└── _schemas/<tool_name>_schema.py
```

| Location | Responsibility |
| --- | --- |
| `__init__.py` | Public façade |
| `_i18n.py` | Result and error messages |
| `_models/` | `@tool` execution function |
| `_schemas/` | LLM-visible description, arguments, types, and defaults |

`@tool(tool_schema=...)` creates a `BaseTool` subclass. Pydantic validates tool-call
arguments and passes every field to the execution function by matching keyword name.
Schema fields and function parameters must therefore agree in name, accepted type, and
default. Put `ctx: ToolContext` first when runtime context is needed.

## The Schema Is the LLM API Contract

The schema class docstring becomes the tool description. Field types, defaults, and
`Field.description` become the argument schema. The LLM cannot read implementation code,
operations, or i18n messages.

A schema docstring should state:

- what the tool does and when to use it
- for a multi-action tool, what each action enables and representative usage
- important constraints and distinctions from similar tools

Each field description should state:

- meaning and required format
- units, ranges, enum values, or coordinate basis
- which actions require it
- default and sentinel meanings
- dependencies on other fields

Exclude internal classes, libraries, dispatch mechanics, and other implementation details
that do not help tool selection or argument generation.

Return `str` for text and `Content` for attachments. Raise `ToolError` for expected
failures that callers should treat as failed tool messages. Some existing tools return a
normal response for recoverable conditions; follow the closest existing contract.

Register the public façade in `_register_tools()` and mirror implementation structure
under `tests/impl/tool_impl/<tool_name>/`. Keep the package, preset, tool-call, and
registration names aligned in snake_case.

## Single-Action Tools

A single-action tool passes schema fields directly to one execution function.

```python
class AudioFileViewSchema(BaseModel):
    """View an audio file."""

    uri_or_file_path: str = Field(description="...")
    start_time: float = Field(default=0.0, description="...")
    end_time: float = Field(default=-1.0, description="...")


@tool(tool_schema=AudioFileViewSchema)
async def AudioFileView(
    ctx: ToolContext,
    uri_or_file_path: str,
    start_time: float = 0.0,
    end_time: float = -1.0,
) -> Content:
    ...
```

Private helpers, services, and utilities may support a complex operation without turning
it into a multi-action tool.

Choose this pattern when the model sees one purpose, most inputs always apply, an action
name adds no useful choice, and results share one flow. File viewers, media generation,
and `change_directory` use this pattern.

## Multi-Action Tools

A multi-action tool groups operations that share a purpose, backend, state, or
post-processing. It adds a closed action type and operation modules.

```text
gui/
├── _models/gui.py
├── _operations/
│   ├── keyboard_press.py
│   └── mouse_move.py
├── _schemas/gui_schema.py
└── _types/action.py
```

### Define a Closed Action Set

```python
Action = Literal["keyboard_press", "mouse_move", "screenshot"]
```

Do not use an unrestricted string. The literal lets Pydantic reject unknown actions and
shows the LLM the complete choice set.

### Use One Shared Schema

```python
class GuiSchema(BaseModel):
    """Understand and operate the GUI."""

    action: Action = Field(description="...")
    key: str = Field(default="", description="Required for keyboard_press")
    x: int = Field(default=-1, description="Required for mouse actions")
    y: int = Field(default=-1, description="Required for mouse actions")
```

The current pattern uses a combined schema rather than a discriminated union. Give
action-specific fields defaults, document their action requirements, and validate them in
the operation.

### Standardize Operation Interfaces

```python
async def keyboard_press(ctx: ToolContext, args: GuiSchema) -> str:
    if not args.key:
        raise ToolError("...")
    ...
```

Operations own action-specific validation and behavior. They should not branch on other
actions or own tool-wide post-processing.

### Keep the Entry Point Focused on Dispatch

```python
_OPERATIONS: dict[Action, Callable[[ToolContext, GuiSchema], Awaitable[str]]] = {
    "keyboard_press": keyboard_press,
    "mouse_move": mouse_move,
    "screenshot": screenshot,
}
```

The `@tool` function reconstructs the schema, dispatches through the typed table, and
applies common pre- or post-processing. If operation outputs and lifecycle stop sharing
meaningful behavior, split the tool.

Chrome, GUI, web, subprocess, and text-file editing use this pattern. Chrome operations
validate input before acquiring one exclusive session and always release the lease after
the action; see [Chrome Tool and Chrome Bridge](chrome-tool-and-bridge.md).

## Testing

Exercise tools through `BaseTool.run()` or `run_tool()`, including the decorator-created
boundary.

For every tool, test successful output, defaults, and major failure or retry paths. For
multi-action tools, also test every action's dispatch, required fields, common processing,
and external-call arguments.

Update the action literal, schema, function signature, dispatch keys, and tests together.
Types alone do not prove dispatch-table completeness.

## Adding a Tool

1. Choose single-action or multi-action based on the model-visible purpose.
2. Create the package, façade, i18n, schema, and `@tool` entry point.
3. For multi-action tools, add the action literal, operations, and typed dispatch table.
4. Align every schema field with the execution function.
5. Decide whether expected failures are normal output or `ToolError`.
6. Register the preset in `_register_tools()`.
7. Add tests through the real tool boundary.
8. Review the docstring and every field description as the LLM-visible API contract.
