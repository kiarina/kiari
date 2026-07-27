import re
from collections.abc import Iterable

from prompt_toolkit.completion import CompleteEvent, Completer, Completion, PathCompleter
from prompt_toolkit.document import Document

from kiari.cli.console.slash_command import slash_command_registry

_PATH_COMPLETION_PREFIXES = ("./", "../", "~/", "/")


class ConsoleCompleter(Completer):
    """Completes slash commands and explicit file path tokens."""

    def __init__(self) -> None:
        self._path_completer: PathCompleter | None = None

    @property
    def path_completer(self) -> PathCompleter:
        if self._path_completer is None:
            self._path_completer = PathCompleter(expanduser=True)

        return self._path_completer

    def get_completions(
        self,
        document: Document,
        complete_event: CompleteEvent,
    ) -> Iterable[Completion]:
        if command_text := _get_command_completion_text(document):
            yield from self._get_command_completions(command_text)
            return

        if path_text := _get_path_completion_text(document):
            path_document = Document(path_text, len(path_text))
            yield from self.path_completer.get_completions(
                path_document,
                complete_event,
            )

    def _get_command_completions(
        self,
        command_text: str,
    ) -> Iterable[Completion]:
        words = [
            f"/{word}"
            for word in (
                slash_command_registry.list_names() + slash_command_registry.list_aliases()
            )
        ]

        for word in sorted(words):
            if word.startswith(command_text):
                yield Completion(word, start_position=-len(command_text))


def _get_command_completion_text(document: Document) -> str | None:
    if document.cursor_position_row != 0:
        return None

    text_before_cursor = document.text_before_cursor
    first_line_before_cursor = text_before_cursor.split("\n", 1)[0]

    if not first_line_before_cursor.startswith("/"):
        return None

    if re.search(r"\s", first_line_before_cursor):
        return None

    return first_line_before_cursor


def _get_path_completion_text(document: Document) -> str | None:
    match = re.search(r"\S+$", document.text_before_cursor)

    if match is None:
        return None

    path_text = match.group(0)

    if path_text.startswith(_PATH_COMPLETION_PREFIXES):
        return path_text

    return None
