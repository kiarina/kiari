from pathlib import Path

from prompt_toolkit.completion import CompleteEvent
from prompt_toolkit.document import Document

from kiari.cli.console._services.console_completer import ConsoleCompleter


def _complete_texts(completer: ConsoleCompleter, text: str) -> list[str]:
    return [
        completion.text
        for completion in completer.get_completions(
            Document(text, len(text)),
            CompleteEvent(),
        )
    ]


def test_completes_slash_command_names_and_aliases() -> None:
    completions = _complete_texts(ConsoleCompleter(), "/a")

    assert "/attach" in completions
    assert "/a" in completions


def test_completes_path_tokens(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    tmp_path.joinpath("alpha.txt").write_text("")

    completions = _complete_texts(ConsoleCompleter(), "please read ./alp")

    assert "ha.txt" in completions


def test_does_not_complete_plain_words_as_paths(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    tmp_path.joinpath("alpha.txt").write_text("")

    completions = _complete_texts(ConsoleCompleter(), "please read alp")

    assert completions == []


def test_completes_command_args_as_paths(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    tmp_path.joinpath("alpha.txt").write_text("")

    completions = _complete_texts(ConsoleCompleter(), "/attach ./alp")

    assert "ha.txt" in completions


def test_completes_content_lines_as_paths(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    tmp_path.joinpath("alpha.txt").write_text("")

    completions = _complete_texts(ConsoleCompleter(), "/run\nplease read ./alp")

    assert "ha.txt" in completions
