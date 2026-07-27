from rich_click.utils import OptionGroupDict

CONSOLE_OPTION_GROUP: OptionGroupDict = {
    "name": "Console",
    "options": [
        "--attachment",
        "--stdin",
        "--editing-mode",
        "--vi",
        "--emacs",
        "--console-handler",
        "--stt",
        "--stt-auto-send-after",
        "--audio-source",
        "--vad-model",
        "--asr-model",
        "--tts",
        "--tts-model",
    ],
}
