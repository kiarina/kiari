from kiarina.i18n import I18n


class ToolInfoSlashCommandI18n(I18n, scope="kiari.cli.console.slash_command_impl.tool_info"):
    description: str = (
        "Manage history tool infos.\n\n"
        "  [cyan]/tool_info[/cyan]                         "
        "Show this help\n"
        "  [cyan]/tool_info list[/cyan]                    "
        "List history tool infos\n"
        "  [cyan]/tool_info add[/cyan]                     "
        "Show tool info specifier examples\n"
        "  [cyan]/tool_info add[/cyan] [yellow]<tool_info_specifier>...[/yellow]    "
        "Add or replace tool infos in history\n"
        "  [cyan]/tool_info remove[/cyan]                  "
        "Select tool infos to remove\n"
        "  [cyan]/tool_info show[/cyan]                    "
        "Select a tool info to show as JSON\n"
        "  [cyan]/tool_info edit[/cyan]                    "
        "Select a tool info to edit as JSON\n"
        "  [cyan]/tool_info arrange[/cyan]                 "
        "Reorder and/or change states by editing the list\n"
    )
    add_examples: str = (
        "Specify tool infos using one of these formats:\n\n"
        "  [dim]/tool_info add run[/dim]\n"
        "  [dim]/tool_info add active:run disabled:browser[/dim]\n"
        '  [dim]/tool_info add \'{"name": "hello", "description": "Say hello"}\'[/dim]'
    )
    no_tool_infos: str = "No tool infos"
    select_tool_infos_to_delete: str = "Select tool infos to delete:"
    select_tool_info_to_show: str = "Select a tool info to show:"
    select_tool_info_to_edit: str = "Select a tool info to edit:"
    deleted_n_tool_infos: str = "Deleted {n} tool infos"
    added_n_tool_infos: str = "Added {n} tool infos"
    edit_cancelled: str = "Edit cancelled"
    edit_no_change: str = "No change"
    tool_info_updated: str = "Tool info {index} updated"
    validation_error: str = "Validation error:\n{error}"
    arrange_instruction: str = (
        "Swap lines to reorder. "
        "Change the leading state (active / inactive / disabled) to toggle. "
        "Do not add or remove lines."
    )
    arrange_cancelled: str = "Arrange cancelled"
    arrange_no_change: str = "No change"
    arranged: str = "Updated tool infos"
    arrange_invalid_line: str = "Line {line_no}: expected '<state> <name>'"
    arrange_invalid_state: str = (
        "Line {line_no}: invalid state '{state}' (must be active, inactive, or disabled)"
    )
    arrange_unknown_name: str = "Line {line_no}: unknown tool name '{name}'"
    arrange_duplicate_name: str = "Duplicate tool name: {name}"
    arrange_missing_names: str = "Missing tool names: {names}"
    unknown_subcommand: str = "Unknown tool_info command: {command}"
