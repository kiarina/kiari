from kiarina.i18n import I18n


class ToolChoiceSlashCommandI18n(I18n, scope="kiari.cli.console.slash_command_impl.tool_choice"):
    description: str = (
        "Set the tool choice policy for this console session.\n\n"
        "  [cyan]/tool_choice[/cyan]                           "
        "Select tool_choice from available tools\n"
        "  [cyan]/tool_choice[/cyan] [yellow]<tool_choice>[/yellow]    "
        "Set tool_choice to auto, any, or a tool name\n\n"
        "  [dim]Examples:[/dim]\n"
        "    [dim]/tool_choice auto[/dim]\n"
        "    [dim]/tool_choice any[/dim]\n"
        "    [dim]/tool_choice hello[/dim]"
    )
    select_tool_choice: str = "Select tool_choice:"
    tool_choice_updated: str = "tool_choice updated: {tool_choice}"
