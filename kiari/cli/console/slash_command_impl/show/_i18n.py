from kiarina.i18n import I18n


class ShowSlashCommandI18n(I18n, scope="kiari.cli.console.slash_command_impl.show"):
    description: str = (
        "Show event history.\n\n"
        "  [cyan]/show[/cyan]                   Show all events\n"
        "  [cyan]/show[/cyan] [yellow]<target>[/yellow]          Filter by event type\n"
        "  [cyan]/show[/cyan] [yellow]<target> <range>[/yellow]  Filter and slice\n\n"
        "  [dim]Target (EventType filter):[/dim]\n"
        "    [dim]a: ai_message  h: human_message  t: tool_message[/dim]\n"
        "    [dim]c: custom      *: all (default)[/dim]\n\n"
        "  [dim]Range (Python slice notation):[/dim]\n"
        "    [dim]0:5  -10:  :10[/dim]"
    )
    no_history: str = "No history"
    no_matching_events: str = "No matching events found"
    invalid_range: str = "Invalid range format: {range}"
