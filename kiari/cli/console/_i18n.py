from kiarina.i18n import I18n


class ConsoleI18n(I18n, scope="kiari.cli.console"):
    command_help: str = "Run LLM agents in an interactive console session."
    texts_help: str = (
        "Initial input text to send as the first user message. Multiple values are "
        "joined with spaces and combined with Markdown body text when provided."
    )
    attachments_help: str = (
        "File, URI, GitHub source, or file pattern to attach to the initial user "
        "message. Repeatable."
    )
    console_handler_help: str = (
        "ConsoleHandler name or config string to run. "
        "Example: 'vanilla' or 'vanilla?key1=value1&key2=value2'."
    )
    tts_help: str = "Enable text-to-speech for console AI responses."
    tts_model_help: str = (
        "TTS model name or config string to use. Example: 'openai' or 'openai?voice=alloy'."
    )
    stt_help: str = "Enable speech-to-text for console user input."
    stt_auto_send_after_help: str = (
        "Automatically send STT input after this many seconds without another "
        "transcript once some text has been recognized."
    )
    audio_source_help: str = "Audio source name or config string to use."
    vad_model_help: str = "VAD model name or config string to use."
    asr_model_help: str = "ASR model name or config string to use."
    editing_mode_help: str = "Editing mode for interactive console input."
    vi_help: str = "Use vi editing mode for interactive console input."
    emacs_help: str = "Use emacs editing mode for interactive console input."
    stdin_help: str = (
        "Read standard input and use it as either an initial human message body "
        "or a system message."
    )
    help_hint: str = "Type /help for commands, Ctrl+C to exit. Option+Enter to send."
    no_input_help: str = "No input provided."
    unknown_command_help: str = "Unknown console command: /{command_name}"
    no_interactive_terminal_error: str = (
        "Error: No interactive terminal detected. "
        "The console interface requires an interactive terminal to run."
    )
