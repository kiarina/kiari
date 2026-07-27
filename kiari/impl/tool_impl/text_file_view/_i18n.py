from kiarina.i18n import I18n


class TextFileViewI18n(I18n, scope="kiari.impl.tool_impl.text_file_view"):
    result: str = "Viewed the file successfully."
    not_found_error: str = (
        "Error: '{file_path}' was not found.\n\nPlease specify an existing file path and try again."
    )
    directory_error: str = (
        "Error: '{file_path}' is a directory, not a file.\n\n"
        "The directory contains the following files:\n"
        "{file_list}\n\n"
        "Please specify a file path and try again."
    )
