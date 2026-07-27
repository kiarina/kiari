from kiarina.i18n import I18n


class FileInfoSlashCommandI18n(I18n, scope="kiari.cli.console.slash_command_impl.file_info"):
    description: str = (
        "Manage history file infos.\n\n"
        "  [cyan]/file_info[/cyan]                         "
        "Show this help\n"
        "  [cyan]/file_info list[/cyan]                    "
        "List history file infos\n"
        "  [cyan]/file_info add[/cyan]                     "
        "Show file info specifier examples\n"
        "  [cyan]/file_info add[/cyan] [yellow]<file_info_source>...[/yellow]    "
        "Add file infos to history\n"
        "  [cyan]/file_info remove[/cyan]                  "
        "Select file infos to remove\n"
        "  [cyan]/file_info show[/cyan]                    "
        "Select a file info to show as JSON\n"
        "  [cyan]/file_info edit[/cyan]                    "
        "Select a file info to edit as JSON\n"
    )
    add_examples: str = (
        "Specify file infos using one of these formats:\n\n"
        "  [dim]/file_info add README.md[/dim]\n"
        "  [dim]/file_info add README.md pyproject.toml[/dim]\n"
        "  [dim]/file_info add src/?include=*.py[/dim]\n"
        '  [dim]/file_info add \'{"uri_or_file_path": "README.md"}\'[/dim]'
    )
    no_file_infos: str = "No file infos"
    no_files_found: str = "No files found"
    select_file_infos_to_delete: str = "Select file infos to delete:"
    select_file_info_to_show: str = "Select a file info to show:"
    select_file_info_to_edit: str = "Select a file info to edit:"
    deleted_n_file_infos: str = "Deleted {n} file infos"
    added_n_file_infos: str = "Added {n} file infos"
    edit_cancelled: str = "Edit cancelled"
    edit_no_change: str = "No change"
    file_info_updated: str = "File info {index} updated"
    validation_error: str = "Validation error:\n{error}"
    unknown_subcommand: str = "Unknown file_info command: {command}"
