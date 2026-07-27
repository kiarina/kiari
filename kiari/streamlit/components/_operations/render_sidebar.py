import asyncio

import streamlit as st
import yaml
from pydantic import ValidationError

from kiari.streamlit import StreamlitIdentity
from kiari.streamlit._constants import (
    STREAMLIT_SELECTED_AGENT_ID_KEY,
    STREAMLIT_SESSION_KEY,
)
from kiari.streamlit.agent_store import AgentStore, AgentUnavailableError
from kiari.streamlit.authenticator import StreamlitAuthenticator
from kiari.streamlit.streamlit_handler import StreamlitHandler, StreamlitSession


def render_sidebar(
    handler: StreamlitHandler,
    authenticator: StreamlitAuthenticator,
    identity: StreamlitIdentity,
    agent_store: AgentStore,
) -> str | None:
    organization_id = handler.run_options.organization_id
    records = agent_store.list(organization_id, identity)
    agent_ids = [record.agent_id for record in records]

    with st.sidebar:
        st.header("🤖 Agents")
        selected = st.selectbox(
            "Agent",
            options=agent_ids,
            index=_selected_index(agent_ids),
            placeholder="Create an agent",
        )
        if selected != st.session_state.get(STREAMLIT_SELECTED_AGENT_ID_KEY):
            st.session_state[STREAMLIT_SELECTED_AGENT_ID_KEY] = selected
            st.session_state.pop(STREAMLIT_SESSION_KEY, None)

        default_agent_id = (
            handler.run_options.agent_id if handler.run_options.agent_id != "default" else ""
        )
        new_agent_id = st.text_input("New agent ID", value=default_agent_id)
        if st.button("Create agent", use_container_width=True):
            try:
                if asyncio.run(handler.has_history(identity, new_agent_id)):
                    raise AgentUnavailableError("Agent ID has unmanaged history")
                agent_store.create(new_agent_id, organization_id, identity)
                st.session_state[STREAMLIT_SELECTED_AGENT_ID_KEY] = new_agent_id
                st.session_state.pop(STREAMLIT_SESSION_KEY, None)
                st.rerun()
            except (AgentUnavailableError, ValidationError, ValueError) as e:
                st.error(str(e))

        if selected:
            _render_delete(handler, identity, agent_store, selected)

        st.divider()
        session = st.session_state.get(STREAMLIT_SESSION_KEY)
        if isinstance(session, StreamlitSession) and selected:
            _render_config(handler, session)
            _render_history(handler, session)

        st.divider()
        st.caption(f"Signed in as {identity.display_name}")
        if identity.authenticator_name == "oidc":
            st.button("Log out", on_click=authenticator.logout, use_container_width=True)

    return selected


def _selected_index(agent_ids: list[str]) -> int | None:
    current = st.session_state.get(STREAMLIT_SELECTED_AGENT_ID_KEY)
    return agent_ids.index(current) if current in agent_ids else None


def _render_delete(
    handler: StreamlitHandler,
    identity: StreamlitIdentity,
    agent_store: AgentStore,
    agent_id: str,
) -> None:
    confirmed = st.checkbox("Confirm agent deletion", key=f"confirm-delete-{agent_id}")
    if st.button("Delete agent", disabled=not confirmed, use_container_width=True):
        try:
            record = agent_store.get_owned(agent_id, handler.run_options.organization_id, identity)
            session = st.session_state.get(STREAMLIT_SESSION_KEY)
            if (
                not isinstance(session, StreamlitSession)
                or session.run_context.agent_id != agent_id
            ):
                session = asyncio.run(handler.create_session(identity, agent_id))
            asyncio.run(handler.delete_history(session))
            agent_store.delete(record)
            st.session_state.pop(STREAMLIT_SELECTED_AGENT_ID_KEY, None)
            st.session_state.pop(STREAMLIT_SESSION_KEY, None)
            st.rerun()
        except Exception as e:
            st.error(str(e))


def _render_config(handler: StreamlitHandler, session: StreamlitSession) -> None:
    st.subheader("⚙️ Run configuration")
    key = f"run-config-{session.run_context.agent_id}"
    if key not in st.session_state:
        st.session_state[key] = ""
    config_text = st.text_area("Session overrides (YAML)", key=key, height=180)
    apply_col, reset_col = st.columns(2)
    if apply_col.button("Apply", use_container_width=True):
        try:
            updates = yaml.safe_load(config_text) or {}
            if not isinstance(updates, dict):
                raise ValueError("Configuration must be a YAML mapping")
            if not all(isinstance(field_name, str) for field_name in updates):
                raise ValueError("Configuration keys must be strings")
            asyncio.run(handler.apply_config(session, updates))
            st.success("Configuration applied")
        except Exception as e:
            st.error(str(e))
    if reset_col.button("Reset", use_container_width=True):
        baseline = {
            key: value
            for key, value in handler.run_options.model_dump().items()
            if key in _editable_fields()
        }
        try:
            asyncio.run(handler.apply_config(session, baseline))
            st.success("Configuration reset")
        except Exception as e:
            st.error(str(e))
    with st.expander("Effective RunOptions"):
        st.json(session.run_options.model_dump(mode="json"))


def _render_history(handler: StreamlitHandler, session: StreamlitSession) -> None:
    st.subheader("📜 History")
    back_col, clear_col = st.columns(2)
    if back_col.button("Back", use_container_width=True):
        try:
            asyncio.run(handler.back(session))
            st.rerun()
        except Exception as e:
            st.error(str(e))
    if clear_col.button("Clear", use_container_width=True):
        try:
            asyncio.run(handler.clear(session))
            st.rerun()
        except Exception as e:
            st.error(str(e))
    transcript = "\n\n".join(event.to_text() for event in session.history.events)
    st.download_button(
        "Download transcript",
        transcript,
        file_name=f"{session.run_context.agent_id}.md",
        mime="text/markdown",
        use_container_width=True,
    )


def _editable_fields() -> set[str]:
    return {
        "agent",
        "file_limits",
        "max_iterations",
        "until_end",
        "until_tool_calls",
        "until_tool_runs",
        "tools",
        "default_tool_state",
        "pre_hooks",
        "post_hooks",
        "workflow",
        "prompt",
        "prompt_limits",
        "system_messages",
        "chat_model",
        "tool_choice",
        "parallel_tool_calls",
        "streaming",
        "tts",
        "tts_model",
        "stt",
        "asr_model",
    }
