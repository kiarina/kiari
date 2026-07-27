from dataclasses import dataclass


@dataclass(frozen=True)
class ReplaceResult:
    new_content: str
    start_line: int
    end_line: int


@dataclass(frozen=True)
class ReplaceError:
    occurrences: int


def replace_str(
    content: str,
    search: str,
    replace: str,
    replace_all: bool = False,
) -> ReplaceResult | ReplaceError:
    # Count the number of occurrences of the search target
    occurrences = content.count(search)

    # If replace_all is False, continue only if the search target is found exactly once
    if not replace_all and occurrences != 1:
        return ReplaceError(occurrences=occurrences)

    # If no occurrences found, return failure
    if occurrences == 0:
        return ReplaceError(occurrences=0)

    if replace_all:
        # Replace all occurrences
        first_pos = content.find(search)
        last_pos = content.rfind(search)

        # Calculate start line (first occurrence)
        start_line = content[:first_pos].count("\n") + 1

        # Calculate end line (last occurrence)
        search_lines = search.count("\n")
        end_line = content[:last_pos].count("\n") + 1 + search_lines

        new_content = content.replace(search, replace)

        return ReplaceResult(
            new_content=new_content,
            start_line=start_line,
            end_line=end_line,
        )
    else:
        # Single replacement
        start_pos = content.find(search)
        end_pos = start_pos + len(search)

        # Identify the start line
        start_line = content[:start_pos].count("\n") + 1

        # Count the number of lines in the search target
        search_lines = search.count("\n")

        # Calculate the end line
        end_line = start_line + search_lines

        new_content = content[:start_pos] + replace + content[end_pos:]

        return ReplaceResult(
            new_content=new_content,
            start_line=start_line,
            end_line=end_line,
        )
