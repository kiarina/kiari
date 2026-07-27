import shlex

from .._schemas.console_text import ConsoleText


def parse_console_text(text: str) -> ConsoleText:
    text = text.strip()

    if not text.startswith("/"):
        return ConsoleText(content=text)

    command_specifier = _parse_command_specifier(text)

    if command_specifier is None:
        return ConsoleText(content=text)

    command_lines, content_lines = _split_command_and_content_lines(
        text,
        command_specifier,
    )
    command_args = _parse_command_args(command_lines)
    content = "\n".join(content_lines).strip()

    return ConsoleText(
        command_specifier=command_specifier,
        command_args=command_args,
        content=content,
    )


def _parse_command_specifier(text: str) -> str | None:
    first_line = text.split("\n", 1)[0]

    if len(first_line) <= 1:
        return None

    return first_line[1:].split(maxsplit=1)[0] or None


def _split_command_and_content_lines(
    text: str,
    command_specifier: str,
) -> tuple[list[str], list[str]]:
    lines = text.split("\n")
    command_lines: list[str] = []
    content_start_index = len(lines)

    for index, line in enumerate(lines):
        if index == 0:
            command_part = line[len(command_specifier) + 1 :].rstrip()
        else:
            command_part = line.rstrip()

        if command_part.endswith("\\"):
            command_lines.append(command_part[:-1].rstrip())
            continue

        command_lines.append(command_part)
        content_start_index = index + 1
        break

    return command_lines, lines[content_start_index:]


def _parse_command_args(command_lines: list[str]) -> list[str]:
    args_text = " ".join(line for line in command_lines if line).strip()

    if not args_text:
        return []

    return shlex.split(args_text)
