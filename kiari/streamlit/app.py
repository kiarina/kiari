import asyncio

import streamlit as st
from kiarina.utils.app import AppAlreadyConfiguredError, configure

from kiari.streamlit._constants import STREAMLIT_SESSION_KEY
from kiari.streamlit._helpers.load_streamlit_startup_options import (
    load_streamlit_startup_options,
)
from kiari.streamlit._helpers.setup_streamlit_runtime import (
    StreamlitRuntime,
    setup_streamlit_runtime,
)
from kiari.streamlit.agent_store import AgentStore, AgentUnavailableError
from kiari.streamlit.authenticator import streamlit_authenticator_registry
from kiari.streamlit.components import render_chat, render_sidebar
from kiari.streamlit.streamlit_handler import StreamlitSession

startup_options = load_streamlit_startup_options()
run_options = startup_options.run_options

st.set_page_config(
    page_title=run_options.streamlit_title,
    page_icon=run_options.streamlit_icon,
    layout=run_options.streamlit_layout,
)


@st.cache_resource
def _get_runtime() -> StreamlitRuntime:
    try:
        configure(app_author="kiarina", app_name="kiari")
    except AppAlreadyConfiguredError:
        pass
    return asyncio.run(setup_streamlit_runtime(startup_options))


@st.cache_resource
def _get_agent_store() -> AgentStore:
    return AgentStore()


runtime = _get_runtime()
handler = runtime.handler
authenticator = streamlit_authenticator_registry.resolve(run_options.streamlit_authenticator)
identity = authenticator.authenticate()

if identity is None:
    st.stop()

st.title(run_options.streamlit_title)
agent_store = _get_agent_store()
selected_agent_id = render_sidebar(handler, authenticator, identity, agent_store)

if not selected_agent_id:
    st.info("Create or select an agent to start.")
    st.stop()

try:
    agent_store.get_owned(selected_agent_id, run_options.organization_id, identity)
except AgentUnavailableError as e:
    st.session_state.pop(STREAMLIT_SESSION_KEY, None)
    st.error(str(e))
    st.stop()

session = st.session_state.get(STREAMLIT_SESSION_KEY)
if not isinstance(session, StreamlitSession) or session.run_context.agent_id != selected_agent_id:
    session = asyncio.run(handler.create_session(identity, selected_agent_id))
    st.session_state[STREAMLIT_SESSION_KEY] = session

render_chat(handler, session, identity)
