from kiarina.i18n import I18n


class STTSlashCommandI18n(I18n, scope="kiari.cli.console.slash_command_impl.stt"):
    description: str = (
        "Toggle speech-to-text input for this console session.\n\n"
        "  [cyan]/stt[/cyan]                     Toggle STT input\n"
        "  [cyan]/stt[/cyan] [yellow]on[/yellow]     Enable STT input\n"
        "  [cyan]/stt[/cyan] [yellow]off[/yellow]    Disable STT input"
    )
    invalid_mode: str = "Usage: /stt on|off"
    stt_enabled: str = "STT enabled"
    stt_disabled: str = "STT disabled"
