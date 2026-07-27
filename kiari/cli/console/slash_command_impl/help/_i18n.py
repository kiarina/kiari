from kiarina.i18n import I18n


class HelpSlashCommandI18n(I18n, scope="kiari.cli.console.slash_command_impl.help"):
    description: str = "Show available slash commands"
    table_title: str = "Available Commands"
    column_command: str = "Command"
    column_description: str = "Description"
    no_description: str = "(no description)"
