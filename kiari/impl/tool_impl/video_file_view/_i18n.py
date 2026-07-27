from kiarina.i18n import I18n


class VideoFileViewI18n(I18n, scope="kiari.impl.tool_impl.video_file_view"):
    result: str = "Viewed the video file successfully."
    not_found_error: str = (
        "Error: '{uri_or_file_path}' was not found.\n\n"
        "Please specify an existing file path and try again."
    )
    not_video_error: str = (
        "Error: '{uri_or_file_path}' is not a video file.\n\n"
        "Please specify a video file and try again."
    )
