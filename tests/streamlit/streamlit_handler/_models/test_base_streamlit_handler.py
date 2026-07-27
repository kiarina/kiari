import pytest

from kiari.core.profile import RunOptions
from kiari.impl.streamlit_handler_impl.vanilla import VanillaStreamlitHandler
from kiari.streamlit import StreamlitIdentity


@pytest.fixture
def handler() -> VanillaStreamlitHandler:
    value = VanillaStreamlitHandler(
        "test",
        RunOptions(no_load=True, no_save=True, cost_recorder="null"),
    )
    value.name = "vanilla"
    return value


async def test_session_uses_authenticated_user_and_selected_agent(handler) -> None:
    identity = StreamlitIdentity(
        user_id="alice",
        display_name="Alice",
        authenticator_name="test",
    )
    session = await handler.create_session(identity, "agent-1")
    assert session.run_context.user_id == "alice"
    assert session.run_context.agent_id == "agent-1"


async def test_apply_config_allows_session_fields_only(handler) -> None:
    identity = StreamlitIdentity(
        user_id="alice",
        display_name="Alice",
        authenticator_name="test",
    )
    session = await handler.create_session(identity, "agent-1")
    await handler.apply_config(session, {"max_iterations": 2, "streaming": False})
    assert session.run_options.max_iterations == 2
    assert session.run_options.streaming is False
    with pytest.raises(ValueError, match="cannot be changed"):
        await handler.apply_config(session, {"history_repository": "local"})
