from kiarina.i18n import I18n


class ImageFileViewI18n(I18n, scope="kiari.impl.tool_impl.image_file_view"):
    result: str = "Viewed the image file successfully."
    not_found_error: str = (
        "Error: '{uri_or_file_path}' was not found.\n\n"
        "Please specify an existing file path and try again."
    )
    not_image_error: str = (
        "Error: '{uri_or_file_path}' is not an image file.\n\n"
        "Please specify an image file and try again."
    )
