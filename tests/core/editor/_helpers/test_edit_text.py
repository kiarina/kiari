from kiari.core.editor import edit_text


async def test_prompt_toolkit(monkeypatch) -> None:
    captured: dict[str, object] = {}

    async def fake_inline(initial, *, editing_mode):
        if initial == "cancel":
            return None

        captured["initial"] = initial
        captured["editing_mode"] = editing_mode
        return initial.replace("hello", "hi")

    monkeypatch.setattr(
        "kiari.core.editor._helpers.edit_text._edit_with_prompt_toolkit",
        fake_inline,
    )

    result = await edit_text("hello", editing_mode="vi")

    assert captured["initial"] == "hello"
    assert captured["editing_mode"] == "vi"
    assert result == "hi"

    captured.clear()
    result = await edit_text("cancel")

    assert result is None
    assert captured == {}


async def test_external_editor(monkeypatch) -> None:
    captured: dict[str, object] = {}

    async def fake_external(initial, *, extension):
        if initial == "cancel":
            return None

        captured["initial"] = initial
        captured["extension"] = extension
        return initial + " edited"

    monkeypatch.setattr(
        "kiari.core.editor._helpers.edit_text._edit_with_external_editor",
        fake_external,
    )

    long_text = "x" * 10_000
    result = await edit_text(long_text, extension=".json")

    assert captured["initial"] == long_text
    assert captured["extension"] == ".json"
    assert result == long_text + " edited"

    captured.clear()
    result = await edit_text("cancel")
    assert result is None
    assert captured == {}
