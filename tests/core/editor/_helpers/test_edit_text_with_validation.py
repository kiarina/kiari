import pytest
from rich.text import Text

from kiari.core.editor import ValidationResult, edit_text_with_validation


class FakeQuestion:
    def __init__(self, selected):
        self.selected = selected

    async def ask_async(self):
        return self.selected


def _always_valid(text: str) -> ValidationResult:
    return ValidationResult(valid=True)


def _always_invalid(text: str) -> ValidationResult:
    return ValidationResult(valid=False, message=Text("invalid", style="red"))


async def test_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_edit_text(initial, **kwargs):
        return None

    monkeypatch.setattr(
        "kiari.core.editor._helpers.edit_text_with_validation.edit_text",
        fake_edit_text,
    )

    result = await edit_text_with_validation("hello", validator=_always_valid)
    assert result is None


async def test_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_edit_text(initial, **kwargs):
        return initial + " world"

    monkeypatch.setattr(
        "kiari.core.editor._helpers.edit_text_with_validation.edit_text",
        fake_edit_text,
    )

    result = await edit_text_with_validation("hello", validator=_always_valid)
    assert result == "hello world"


async def test_invalid(
    monkeypatch: pytest.MonkeyPatch,
    setup_run_context,
) -> None:
    progress = 0

    async def fake_edit_text(initial, **kwargs):
        return initial + " world"

    monkeypatch.setattr(
        "kiari.core.editor._helpers.edit_text_with_validation.edit_text",
        fake_edit_text,
    )

    def fake_select(*args, **kwargs):
        nonlocal progress
        progress += 1

        match progress:
            case 1:
                return FakeQuestion("continue")
            case 2:
                return FakeQuestion("reset")
            case 3:
                return FakeQuestion("abort")
            case _:
                raise AssertionError("Too many iterations in test_invalid")

    monkeypatch.setattr("questionary.select", fake_select)

    result = await edit_text_with_validation("hello", validator=_always_invalid)
    assert result is None
    assert progress == 3
