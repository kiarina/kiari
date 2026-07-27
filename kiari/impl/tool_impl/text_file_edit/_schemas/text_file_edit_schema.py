from pydantic import BaseModel, Field

from .._types.action import Action


class TextFileEditSchema(BaseModel):
    """
    Create and edit text files.

    Supports the following actions:
    - create: Create a new file (errors if the file already exists)
      Required arguments: file_path, content
    - update: Overwrite an existing file (errors if the file does not exist)
      Required arguments: file_path, content
    - line_replace: Replace or add the specified lines
      Required arguments: file_path, start_line, end_line, replace
    - str_replace: Search for and replace strings
      Required arguments: file_path, search, replace
    """

    action: Action = Field(
        description=(
            "Action to execute\n"
            '- "create": Create a new file. Errors if it already exists '
            "(Required arguments: content)\n"
            '- "update": Overwrite an existing file. Errors if it does not exist '
            "(Required arguments: content)\n"
            '- "line_replace": Replace or add the specified lines '
            "(Required arguments: start_line, end_line, replace)\n"
            '- "str_replace": Search for and replace strings '
            "(Required arguments: search, replace)"
        ),
    )

    # --------------------------------------------------
    # Common for all actions
    # --------------------------------------------------

    file_path: str = Field(description="File path to edit (for all actions)")

    # --------------------------------------------------
    # create / update action arguments
    # --------------------------------------------------

    content: str = Field(
        default="",
        description="Content to write (for create and update actions)",
    )

    # --------------------------------------------------
    # line_replace action arguments
    # --------------------------------------------------

    start_line: int = Field(
        default=1,
        description=(
            "Start line number of the replacement range. Line 1 is 1. "
            "0 to insert at the beginning. -1 to append at the end "
            "(for line_replace action)"
        ),
    )

    end_line: int = Field(
        default=1,
        description=(
            "End line number of the replacement range. Line 1 is 1. "
            "0 to insert at the beginning. -1 to append at the end "
            "(for line_replace action)"
        ),
    )

    replace: str = Field(
        default="",
        description="String to replace (for line_replace and str_replace actions)",
    )

    # --------------------------------------------------
    # str_replace action arguments
    # --------------------------------------------------

    search: str = Field(
        default="",
        description="String to search for (for str_replace action)",
    )

    replace_all: bool = Field(
        default=False,
        description=(
            "Whether to replace all occurrences of the search string. "
            "If False, only a unique match is allowed (for str_replace action)"
        ),
    )
