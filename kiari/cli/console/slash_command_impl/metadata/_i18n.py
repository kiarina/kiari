from kiarina.i18n import I18n


class MetadataSlashCommandI18n(I18n, scope="kiari.cli.console.slash_command_impl.metadata"):
    description: str = (
        "Manage history metadata.\n\n"
        "  [cyan]/metadata[/cyan]                       "
        "Show this help\n"
        "  [cyan]/metadata list[/cyan]                  "
        "List metadata entries with previews\n"
        "  [cyan]/metadata set[/cyan]                   "
        "Show set examples\n"
        "  [cyan]/metadata set[/cyan] [yellow]<key>[/yellow] [yellow]<json_value>[/yellow]   "
        "Set value for the key\n"
        "  [cyan]/metadata delete[/cyan]                "
        "Select keys to delete\n"
        "  [cyan]/metadata show[/cyan]                  "
        "Select a key to show value as JSON\n"
        "  [cyan]/metadata edit[/cyan]                  "
        "Select a key to edit value as JSON\n"
    )
    set_examples: str = (
        "Usage:\n\n"
        "  [dim]/metadata set[/dim] [yellow]<key>[/yellow]\n"
        "  [yellow]<json_value>[/yellow]\n\n"
        "Examples:\n\n"
        "  [dim]/metadata set flag[/dim]\n"
        "  [dim]true[/dim]\n\n"
        "  [dim]/metadata set count[/dim]\n"
        "  [dim]42[/dim]\n\n"
        "  [dim]/metadata set ratio[/dim]\n"
        "  [dim]1.5[/dim]\n\n"
        "  [dim]/metadata set name[/dim]\n"
        '  [dim]"fire"[/dim]\n\n'
        "  [dim]/metadata set nothing[/dim]\n"
        "  [dim]null[/dim]\n\n"
        "  [dim]/metadata set tags[/dim]\n"
        '  [dim]["a", "b", "c"][/dim]\n\n'
        "  [dim]/metadata set config[/dim]\n"
        '  [dim]{"host": "localhost", "port": 8080}[/dim]\n\n'
        "Note:\n\n"
        "  - The value must be valid JSON.\n"
        '  - Strings must be quoted: [yellow]"fire"[/yellow], '
        "not [yellow]fire[/yellow]."
    )
    no_metadata: str = "No metadata"
    select_keys_to_delete: str = "Select metadata keys to delete:"
    select_key_to_show: str = "Select a metadata key to show:"
    select_key_to_edit: str = "Select a metadata key to edit:"
    value_required: str = "Value (JSON content) is required"
    invalid_json: str = "Invalid JSON: {error}"
    deleted_n_metadata: str = "Deleted {n} metadata entries"
    metadata_set: str = "Set metadata: {key}"
    metadata_overwritten: str = "Overwrote metadata: {key}"
    metadata_updated: str = "Metadata {key} updated"
    edit_cancelled: str = "Edit cancelled"
    edit_no_change: str = "No change"
    validation_error: str = "Validation error:\n{error}"
    unknown_subcommand: str = "Unknown metadata command: {command}"
