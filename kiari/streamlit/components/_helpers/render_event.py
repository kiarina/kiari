import json
from pathlib import Path
from typing import Any

import streamlit as st
from kiarina.agi.event import Event


def render_event(event: Event) -> None:
    if event.type == "ai_message_chunk" or event.hidden:
        return
    if event.type == "human_message":
        with st.chat_message("user"):
            _render_message(event)
    elif event.type in {"ai_message", "tool_message"}:
        with st.chat_message("assistant"):
            _render_message(event)
    elif event.type == "custom":
        payload = getattr(event, "payload", {})
        if isinstance(payload, dict) and payload.get("type") == "error":
            st.error(payload.get("message", "An error occurred"))
        else:
            st.info(payload)
    else:
        st.write(event.to_text())


def _render_message(event: Event) -> None:
    text = event.to_text().strip()
    if text:
        st.markdown(text)

    message = getattr(event, "message", None)
    for tool_call in getattr(message, "tool_calls", []) or []:
        name = getattr(tool_call, "name", None) or tool_call.get("name", "tool")
        args = getattr(tool_call, "args", None) or tool_call.get("args", {})
        with st.expander(f"🔧 Tool Call: `{name}`"):
            st.code(json.dumps(args, indent=2, ensure_ascii=False), language="json")

    for content in getattr(message, "contents", []) or []:
        for file_info in getattr(content, "files", []) or []:
            _render_file_info(file_info)

    artifact = getattr(message, "artifact", None)
    if artifact:
        data = artifact.model_dump(mode="json") if hasattr(artifact, "model_dump") else artifact
        if isinstance(data, dict):
            for file_info in data.get("file_infos", []):
                _render_file_info(file_info)
            metadata = {key: value for key, value in data.items() if key != "file_infos"}
            if metadata:
                with st.expander("Artifact metadata"):
                    st.json(metadata)


def _render_file_info(file_info: Any) -> None:
    data = file_info.model_dump(mode="python") if hasattr(file_info, "model_dump") else file_info
    if not isinstance(data, dict):
        st.write(data)
        return
    path_value = data.get("uri_or_file_path")
    title = data.get("display_name") or (Path(path_value).name if path_value else "file")
    file_type = data.get("type") or data.get("file_type") or "other"

    if not path_value or not Path(path_value).is_file():
        st.caption(f"[{file_type}] {title}")
        return

    path = Path(path_value)
    if file_type == "image":
        st.image(str(path), caption=title)
    elif file_type == "audio":
        st.audio(str(path))
    elif file_type == "video":
        st.video(str(path))
    elif file_type == "text":
        with st.expander(title):
            st.code(path.read_text(errors="replace"), language="text")
    else:
        st.download_button(
            f"Download {title}",
            data=path.read_bytes(),
            file_name=title,
            mime=data.get("mime_type", "application/octet-stream"),
            key=f"download-{getattr(file_info, 'id', path_value)}",
        )
