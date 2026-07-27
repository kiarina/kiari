from kiarina.i18n import I18n


class ChangeDirectoryI18n(I18n, scope="kiari.impl.tool_impl.change_directory"):
    file_not_found_error: str = "Error: '{dir_path}' directory not found"
    permission_error: str = "Error: Permission denied to access '{dir_path}'"
    not_a_directory_error: str = "Error: '{dir_path}' is not a directory"
    result: str = "Changed current directory to '{dir_path}' successfully."
