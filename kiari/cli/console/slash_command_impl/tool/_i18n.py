from kiarina.i18n import I18n


class ToolSlashCommandI18n(I18n, scope="kiari.cli.console.slash_command_impl.tool"):
    description: str = (
        "Manage tools for this console session.\n\n"
        "  [cyan]/tool[/cyan]                          "
        "Show this help\n"
        "  [cyan]/tool list[/cyan]                     "
        "List current tools\n"
        "  [cyan]/tool add[/cyan]                      "
        "Select tools from the registry to add\n"
        "  [cyan]/tool add[/cyan] [yellow]<tool_specifier>...[/yellow]      "
        "Add tools by specifier (replace if same name)\n"
        "  [cyan]/tool remove[/cyan]                   "
        "Select tools to remove\n\n"
        "  [dim]Examples:[/dim]\n"
        "    [dim]/tool add hello[/dim]\n"
        "    [dim]/tool add hello wait[/dim]\n"
        "    [dim]/tool add hello?name=friend[/dim]\n"
        "    [dim]/tool add wait?duration=3[/dim]"
    )
    no_tools: str = "No tools"
    no_available_tools: str = "No available tools"
    select_tools_to_add: str = "Select tools to add:"
    select_tools_to_delete: str = "Select tools to delete:"
    deleted_n_tools: str = "Deleted {n} tools"
    added_n_tools: str = "Added {n} tools"
    unknown_subcommand: str = "Unknown tool command: {command}"
