from kiarina.i18n import I18n


class TextFileEditI18n(I18n, scope="kiari.impl.tool_impl.text_file_edit"):
    file_not_readable_error: str = "Error: File {file_path} cannot be read"
    file_already_exists_error: str = (
        "Error: File {file_path} already exists. Use action='update' to overwrite an existing file"
    )
    file_not_exists_error: str = (
        "Error: File {file_path} does not exist. Use action='create' to create a new file"
    )
    empty_search_pattern_error: str = (
        "Error: Search pattern is empty. "
        "To edit an existing empty file, use action='update' or action='line_replace'"
    )
    multiple_matches_error: str = (
        "Error: Search pattern found in {count} locations. "
        "Search pattern must be unique. "
        "To replace all occurrences, set replace_all=True"
    )
    pattern_not_found_error: str = "Error: Search pattern not found"
    invalid_start_line_error: str = (
        "Error: Start line number must be 1 or greater "
        "(to insert at the beginning, use start_line=0, end_line=0; "
        "to append at the end, use start_line=-1, end_line=-1). "
        "Specified start line number: {start_line}"
    )
    start_line_exceeds_max_error: str = (
        "Error: Specified start line number {start_line} "
        "exceeds the maximum line count {max_line} of the file"
    )
    invalid_end_line_error: str = (
        "Error: End line number must be 1 or greater "
        "(to insert at the beginning, use start_line=0, end_line=0; "
        "to append at the end, use start_line=-1, end_line=-1). "
        "Specified end line number: {end_line}"
    )
    end_line_exceeds_max_error: str = (
        "Error: Specified end line number {end_line} "
        "exceeds the maximum line count {max_line} of the file"
    )
    start_line_greater_than_end_line_error: str = (
        "Error: Start line number {start_line} "
        "must be less than or equal to end line number {end_line}"
    )
    file_created: str = "Result: Created {file_path}. Attached the resulting file"
    file_updated: str = "Result: Updated {file_path}. Attached the resulting file"
    line_replaced: str = "Result: Replaced lines in {file_path}. Attached the resulting file"
    str_replaced: str = "Result: Replaced string in {file_path}. Attached the resulting file"
