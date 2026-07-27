from kiarina.i18n import I18n


class BackSlashCommandI18n(I18n, scope="kiari.cli.console.slash_command_impl.back"):
    description: str = (
        "Go back in history.\n\n"
        "  [cyan]/back[/cyan]          "
        "Revert to before the last human message\n"
        "  [cyan]/back[/cyan] [yellow]<n>[/yellow]      "
        "Delete last n events from history"
    )
    no_history: str = "No history exists"
    invalid_n: str = "n must be a positive integer"
    all_history_deleted: str = "All history has been deleted"
    deleted_n_events: str = "Deleted {n} events from history"
    reverted_to_previous: str = "History has been reverted to the previous state"
    no_human_message: str = "No human message found in history"
