from kiarina.i18n import I18n


class AudioFileViewI18n(I18n, scope="kiari.impl.tool_impl.audio_file_view"):
    result: str = "Viewed the audio file successfully."
    not_found_error: str = (
        "Error: '{uri_or_file_path}' was not found.\n\n"
        "Please specify an existing file path and try again."
    )
    not_audio_error: str = (
        "Error: '{uri_or_file_path}' is not an audio file.\n\n"
        "Please specify an audio file and try again."
    )
