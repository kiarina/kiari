from kiarina.i18n import I18n


class GuiI18n(I18n, scope="kiari.impl.tool_impl.gui"):
    keyboard_press_requires_key_error: str = "Error: keyboard_press action requires key"
    keyboard_hotkey_requires_keys_error: str = "Error: keyboard_hotkey action requires keys"
    keyboard_write_requires_text_error: str = "Error: keyboard_write action requires text"
    mouse_move_requires_coordinates_error: str = (
        "Error: mouse_move action requires x, y coordinates"
    )

    keyboard_press_result: str = (
        "Pressed and released key '{key}'.\n"
        "Retrieved a screenshot of the monitor after the key operation, please check it."
    )
    keyboard_hotkey_result: str = (
        "Pressed hotkey {keys}.\n"
        "Retrieved a screenshot of the monitor after the hotkey operation, please check it."
    )
    keyboard_write_result: str = (
        "Inputted text '{text}'.\n"
        "Retrieved a screenshot of the monitor after the text input, please check it."
    )
    mouse_click_result: str = (
        "Executed {action_name}.\n"
        "Retrieved a screenshot of the monitor after the click, please check it."
    )
    mouse_down_result: str = (
        "Executed {action_name}.\n"
        "Retrieved a screenshot of the monitor after the button press, please check it."
    )
    mouse_move_result: str = (
        "Moved mouse to monitor {monitor_index} coordinates ({x}, {y}) "
        "(movement time: {duration} seconds).\n"
        "Retrieved a screenshot of the monitor after the mouse movement, please check it."
    )
    mouse_up_result: str = (
        "Executed {action_name}.\n"
        "Retrieved a screenshot of the monitor after the button release, please check it."
    )
    screenshot_result: str = (
        "Retrieved a screenshot of the screen.\nPlease check the current state of the monitor."
    )

    left_click: str = "Left click"
    right_click: str = "Right click"
    left_button_press: str = "Left button press"
    right_button_press: str = "Right button press"
    left_button_release: str = "Left button release"
    right_button_release: str = "Right button release"
