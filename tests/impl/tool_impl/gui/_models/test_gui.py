from collections.abc import Awaitable, Callable
from typing import Any
from unittest.mock import MagicMock

from kiarina.agi.message import ToolMessage


async def test_screenshots_attached(
    run_gui: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    gui_mock: MagicMock,
) -> None:
    message = await run_gui({"action": "screenshot"})

    assert not message.failed
    assert message.tool_name == "gui"

    content = message.contents[0]
    assert content.text == (
        "Retrieved a screenshot of the screen.\nPlease check the current state of the monitor."
    )
    assert len(content.files) == 1
    assert content.files[0].type == "image"

    gui_mock.monitor.refresh.assert_called_once()


# --------------------------------------------------
# keyboard_press
# --------------------------------------------------


async def test_keyboard_press(
    run_gui: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    gui_mock: MagicMock,
) -> None:
    message = await run_gui({"action": "keyboard_press", "key": "enter"})

    assert not message.failed
    assert "Pressed and released key 'enter'." in message.contents[0].text
    gui_mock.keyboard.press.assert_called_once_with("enter")


async def test_keyboard_press_requires_key(
    run_gui: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    message = await run_gui({"action": "keyboard_press"})

    assert message.failed
    assert "keyboard_press action requires key" in message.contents[0].text


# --------------------------------------------------
# keyboard_hotkey
# --------------------------------------------------


async def test_keyboard_hotkey(
    run_gui: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    gui_mock: MagicMock,
) -> None:
    message = await run_gui({"action": "keyboard_hotkey", "keys": ["command", "c"]})

    assert not message.failed
    assert "Pressed hotkey" in message.contents[0].text
    gui_mock.keyboard.hotkey.assert_called_once_with("command", "c")


async def test_keyboard_hotkey_requires_keys(
    run_gui: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    message = await run_gui({"action": "keyboard_hotkey"})

    assert message.failed
    assert "keyboard_hotkey action requires keys" in message.contents[0].text


# --------------------------------------------------
# keyboard_write
# --------------------------------------------------


async def test_keyboard_write(
    run_gui: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    gui_mock: MagicMock,
) -> None:
    message = await run_gui({"action": "keyboard_write", "text": "hello"})

    assert not message.failed
    assert "Inputted text 'hello'." in message.contents[0].text
    gui_mock.keyboard.write.assert_called_once_with("hello")


async def test_keyboard_write_requires_text(
    run_gui: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    message = await run_gui({"action": "keyboard_write"})

    assert message.failed
    assert "keyboard_write action requires text" in message.contents[0].text


# --------------------------------------------------
# mouse_click
# --------------------------------------------------


async def test_mouse_click_with_coordinates(
    run_gui: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    gui_mock: MagicMock,
) -> None:
    message = await run_gui({"action": "mouse_click", "monitor_index": 1, "x": 10, "y": 20})

    assert not message.failed
    assert "Left click" in message.contents[0].text
    gui_mock.mouse.move.assert_called_once_with(1, 10, 20, 0.0)
    gui_mock.mouse.click.assert_called_once_with("left")


async def test_mouse_click_right_without_coordinates(
    run_gui: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    gui_mock: MagicMock,
) -> None:
    message = await run_gui({"action": "mouse_click", "button": "right"})

    assert not message.failed
    assert "Right click" in message.contents[0].text
    gui_mock.mouse.move.assert_not_called()
    gui_mock.mouse.click.assert_called_once_with("right")


# --------------------------------------------------
# mouse_down
# --------------------------------------------------


async def test_mouse_down_with_coordinates(
    run_gui: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    gui_mock: MagicMock,
) -> None:
    message = await run_gui({"action": "mouse_down", "monitor_index": 1, "x": 5, "y": 6})

    assert not message.failed
    assert "Left button press" in message.contents[0].text
    gui_mock.mouse.move.assert_called_once_with(1, 5, 6, 0.0)
    gui_mock.mouse.down.assert_called_once_with("left")


async def test_mouse_down_right_without_coordinates(
    run_gui: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    gui_mock: MagicMock,
) -> None:
    message = await run_gui({"action": "mouse_down", "button": "right"})

    assert not message.failed
    assert "Right button press" in message.contents[0].text
    gui_mock.mouse.move.assert_not_called()
    gui_mock.mouse.down.assert_called_once_with("right")


# --------------------------------------------------
# mouse_move
# --------------------------------------------------


async def test_mouse_move(
    run_gui: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    gui_mock: MagicMock,
) -> None:
    message = await run_gui({"action": "mouse_move", "monitor_index": 2, "x": 100, "y": 200})

    assert not message.failed
    assert "Moved mouse to monitor 2 coordinates (100, 200)" in message.contents[0].text
    gui_mock.mouse.move.assert_called_once_with(2, 100, 200, 0.0)


async def test_mouse_move_requires_coordinates(
    run_gui: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    message = await run_gui({"action": "mouse_move"})

    assert message.failed
    assert "mouse_move action requires x, y coordinates" in message.contents[0].text


# --------------------------------------------------
# mouse_up
# --------------------------------------------------


async def test_mouse_up_with_coordinates(
    run_gui: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    gui_mock: MagicMock,
) -> None:
    message = await run_gui({"action": "mouse_up", "monitor_index": 1, "x": 1, "y": 2})

    assert not message.failed
    assert "Left button release" in message.contents[0].text
    gui_mock.mouse.move.assert_called_once_with(1, 1, 2, 0.0)
    gui_mock.mouse.up.assert_called_once_with()


async def test_mouse_up_right_without_coordinates(
    run_gui: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    gui_mock: MagicMock,
) -> None:
    message = await run_gui({"action": "mouse_up", "button": "right"})

    assert not message.failed
    assert "Right button release" in message.contents[0].text
    gui_mock.mouse.move.assert_not_called()
    gui_mock.mouse.up.assert_called_once_with()
