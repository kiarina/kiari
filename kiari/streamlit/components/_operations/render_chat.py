import asyncio
from pathlib import Path

import streamlit as st
from kiarina.agi import asr_model, tts_model

from kiari.lib.audio_utils import load_audio_samples
from kiari.streamlit import StreamlitIdentity
from kiari.streamlit.streamlit_handler import (
    StreamlitHandler,
    StreamlitRequest,
    StreamlitSession,
)

from .._helpers.render_event import render_event
from .._helpers.save_uploads import save_uploads


def render_chat(
    handler: StreamlitHandler,
    session: StreamlitSession,
    identity: StreamlitIdentity,
) -> None:
    for event in session.history.events:
        render_event(event)

    value = st.chat_input(
        "What would you like to know?",
        accept_file="multiple",
        accept_audio=session.run_options.stt,
        key=f"chat-input-{session.run_context.agent_id}",
    )
    if not value:
        return

    text = value.text
    uploaded_files = list(value.files)
    audio = getattr(value, "audio", None)
    if audio is not None:
        uploaded_files.append(audio)
    attachments = save_uploads(
        uploaded_files,
        identity,
        session.run_context.agent_id,
    )

    if audio is not None:
        audio_path = attachments[-1]
        samples, sample_rate = load_audio_samples(audio_path)
        transcribed = asyncio.run(
            asr_model.speech_to_text(
                samples,
                sample_rate,
                asr_options={"asr_model": session.run_options.asr_model},
                cost_recorder=session.cost_recorder,
                run_context=session.run_context,
            )
        ).strip()
        text = "\n\n".join(part for part in (text.strip(), transcribed) if part)
        attachments = attachments[:-1]

    request = StreamlitRequest(text=text, attachments=attachments)

    async def consume() -> None:
        streaming_text = ""
        streaming_placeholder = st.empty()
        async for event in handler.run_request(session, request):
            if event.type == "ai_message_chunk":
                streaming_text += event.to_text()
                streaming_placeholder.markdown(streaming_text + " ▌")
            else:
                if streaming_text:
                    streaming_placeholder.empty()
                    streaming_text = ""
                render_event(event)

    try:
        asyncio.run(consume())
    except Exception as e:
        st.error(str(e))
        return

    if (
        session.run_options.tts
        and session.last_event is not None
        and session.last_event.type == "ai_message"
        and not session.last_event.message.tool_calls
        and (speech_text := session.last_event.to_text().strip())
    ):
        audio_file = asyncio.run(
            tts_model.text_to_speech(
                speech_text,
                tts_options={"tts_model": session.run_options.tts_model},
                cost_recorder=session.cost_recorder,
                run_context=session.run_context,
            )
        )
        if Path(audio_file).is_file():
            st.audio(audio_file, autoplay=True)
        asyncio.run(session.cost_recorder.flush(session.run_context))

    st.rerun()
