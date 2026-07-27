from kiarina.i18n import I18n


class TTSSlashCommandI18n(I18n, scope="kiari.cli.console.slash_command_impl.tts"):
    description: str = (
        "Toggle text-to-speech playback for this console session.\n\n"
        "  [cyan]/tts[/cyan]                     Toggle TTS\n"
        "  [cyan]/tts[/cyan] [yellow]on[/yellow]     Enable TTS\n"
        "  [cyan]/tts[/cyan] [yellow]off[/yellow]    Disable TTS"
    )
    invalid_mode: str = "Usage: /tts on|off"
    tts_enabled: str = "TTS enabled"
    tts_disabled: str = "TTS disabled"
