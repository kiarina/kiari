from streamlit.testing.v1 import AppTest


def test_render_event_message_and_custom_variants() -> None:
    app = AppTest.from_string(
        """
from kiarina.agi.event import AIMessageEvent, CustomEvent, HumanMessageEvent, ToolMessageEvent
from kiarina.agi.message import ToolCall
from kiari.streamlit.components._helpers.render_event import render_event

render_event(HumanMessageEvent.create("hello"))
render_event(AIMessageEvent.create("world", tool_calls=[ToolCall(name="search", args={"q": "x"})]))
render_event(ToolMessageEvent.create("done", tool_call_id="call-1", tool_name="search"))
render_event(CustomEvent.create(type="notice", message="ok"))
"""
    ).run()
    assert not app.exception
    assert len(app.chat_message) == 3
    assert len(app.expander) == 1
    assert app.info
