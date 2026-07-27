import re
import uuid
from pathlib import Path
from typing import Any

from kiarina.utils.app import user_directory

from kiari.streamlit import StreamlitIdentity


def save_uploads(
    uploaded_files: list[Any],
    identity: StreamlitIdentity,
    agent_id: str,
) -> list[str]:
    paths: list[str] = []
    directory = (
        user_directory.get_user_cache_dir() / "streamlit" / "uploads" / identity.user_id / agent_id
    )
    directory.mkdir(parents=True, exist_ok=True)

    for uploaded_file in uploaded_files:
        name = _safe_name(uploaded_file.name)
        path = directory / f"{uuid.uuid4().hex}-{name}"
        path.write_bytes(uploaded_file.getvalue())
        paths.append(str(path))
    return paths


def _safe_name(value: str) -> str:
    name = Path(value).name
    name = re.sub(r"[^a-zA-Z0-9._-]+", "_", name).strip("._")
    return name or "upload"
