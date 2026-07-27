from kiarina.i18n import I18n


class ClearSlashCommandI18n(I18n, scope="kiari.cli.console.slash_command_impl.clear"):
    description: str = (
        "Clear history and terminal display.\n\n"
        "  [cyan]/clear[/cyan]                 Clear all history data\n"
        "  [cyan]/clear[/cyan] [yellow]<targets>[/yellow]     "
        "Clear selected history data\n\n"
        "  [dim]Targets:[/dim]\n"
        "    [dim]e: events  f: file_infos  t: tool_infos  m: metadata[/dim]"
    )
    history_cleared: str = "History cleared"
    invalid_targets: str = "Invalid clear targets: {targets}"
