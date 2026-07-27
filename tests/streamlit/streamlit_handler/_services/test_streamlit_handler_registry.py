from kiari.core.profile import RunOptions
from kiari.impl.streamlit_handler_impl.vanilla import VanillaStreamlitHandler
from kiari.streamlit.streamlit_handler import streamlit_handler_registry


def test_streamlit_handler_registry() -> None:
    handler = streamlit_handler_registry.resolve(
        None, profile_name="test", run_options=RunOptions()
    )
    assert isinstance(handler, VanillaStreamlitHandler)
    assert handler.name == "vanilla"
