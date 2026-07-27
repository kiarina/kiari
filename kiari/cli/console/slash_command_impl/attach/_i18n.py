from kiarina.i18n import I18n


class AttachSlashCommandI18n(I18n, scope="kiari.cli.console.slash_command_impl.attach"):
    description: str = (
        "Manage file attachments for the next message.\n\n"
        "  [cyan]/attach[/cyan]                        "
        "Show this help\n"
        "  [cyan]/attach list[/cyan]                   "
        "List current attachments\n"
        "  [cyan]/attach add[/cyan]                    "
        "Show attachment specifier examples\n"
        "  [cyan]/attach add[/cyan] [yellow]<source>...[/yellow]        "
        "Add files to attachments\n"
        "  [cyan]/attach remove[/cyan]                 "
        "Select files to remove\n"
        "  [cyan]/attach[/cyan] [yellow]<source>...[/yellow]            "
        "Attach files (send if a message follows)"
    )
    add_examples: str = (
        "Specify files using one of these formats:\n\n"
        "  [dim]/attach add ./README.md[/dim]\n"
        "  [dim]/attach add ./README.md ./pyproject.toml[/dim]\n"
        "  [dim]/attach add ./src[/dim]\n"
        "  [dim]/attach add ./**/*.py[/dim]\n"
        "  [dim]/attach add ./src/?include=*.py[/dim]\n"
        "  [dim]/attach add ./src/?exclude=*_test.py[/dim]\n"
        "  [dim]/attach add ./src/?include=*.py&exclude=*_test.py[/dim]\n"
        "  [dim]/attach add @owner/repo/path[/dim]"
    )
    no_attached_files: str = "No attached files"
    no_files_found: str = "No files found"
    select_files_to_delete: str = "Select files to delete:"
    added_n_attached_files: str = "Added {n} attached files"
    deleted_n_attached_files: str = "Deleted {n} attached files"
