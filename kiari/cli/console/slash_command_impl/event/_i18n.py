from kiarina.i18n import I18n


class EventSlashCommandI18n(I18n, scope="kiari.cli.console.slash_command_impl.event"):
    description: str = (
        "Manage history events.\n\n"
        "  [cyan]/event[/cyan]                         "
        "Show this help\n"
        "  [cyan]/event list[/cyan]                    "
        "List history events\n"
        "  [cyan]/event add[/cyan]                     "
        "Show event specifier examples\n"
        "  [cyan]/event add[/cyan] [yellow]<event_specifier>...[/yellow]    "
        "Add events to history\n"
        "  [cyan]/event remove[/cyan]                  "
        "Select events to remove\n"
        "  [cyan]/event show[/cyan]                    "
        "Select an event to show as JSON\n"
        "  [cyan]/event edit[/cyan]                    "
        "Select an event to edit as JSON\n"
    )
    add_examples: str = (
        "Specify events using one of these formats:\n\n"
        "  [dim]/event add hello[/dim]\n"
        "  [dim]/event add hello world[/dim]\n"
        '  [dim]/event add \'{"text": "hello", "files": ["/path/to/file"]}\'[/dim]\n'
        '  [dim]/event add \'["ai", "hello"]\'[/dim]\n'
        '  [dim]/event add \'["ai", {"tool_calls": [{"name": "wait", "args": {"duration": 1}, "id": "1"}]}]\'[/dim]\n'
        '  [dim]/event add \'["tool", {"text": "done", "tool_name": "wait", "tool_call_args": {"duration": 1}, "tool_call_id": "1"}]\'[/dim]\n'
        '  [dim]/event add \'["custom", {"type": "note"}]\'[/dim]'
    )
    no_events: str = "No events"
    select_events_to_delete: str = "Select events to delete:"
    select_event_to_show: str = "Select an event to show:"
    select_event_to_edit: str = "Select an event to edit:"
    deleted_n_events: str = "Deleted {n} events"
    added_n_events: str = "Added {n} events"
    edit_cancelled: str = "Edit cancelled"
    edit_no_change: str = "No change"
    event_updated: str = "Event {index} updated"
    validation_error: str = "Validation error:\n{error}"
    unknown_subcommand: str = "Unknown event command: {command}"
