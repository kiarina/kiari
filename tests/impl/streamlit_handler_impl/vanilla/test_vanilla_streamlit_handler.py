from kiari.core.profile import RunOptions
from kiari.impl.streamlit_handler_impl.vanilla import VanillaStreamlitHandler


def test_vanilla_streamlit_handler() -> None:
    handler = VanillaStreamlitHandler("test", RunOptions())
    handler.name = "vanilla"
    assert handler.name == "vanilla"
