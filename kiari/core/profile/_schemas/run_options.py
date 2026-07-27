from typing import Literal

from pydantic import BaseModel, Field, field_validator


class RunOptions(BaseModel):
    # --------------------------------------------------
    # History Repository
    # --------------------------------------------------
    history_repository: str | None = None
    no_load: bool = False
    no_save: bool = False
    allow_active_missing_tools: bool = False
    # --------------------------------------------------
    # History
    # --------------------------------------------------
    events: list[str] = Field(default_factory=list)
    file_infos: list[str] = Field(default_factory=list)
    tool_infos: list[str] = Field(default_factory=list)
    default_tool_state: Literal["active", "inactive", "disabled"] = "active"
    # --------------------------------------------------
    # Agent
    # --------------------------------------------------
    agent: str | None = None
    file_limits: str | None = None
    max_iterations: int | None = None
    until_end: bool | None = None
    until_tool_calls: list[str] = Field(default_factory=list)
    until_tool_runs: list[str] = Field(default_factory=list)
    # --------------------------------------------------
    # Tool
    # --------------------------------------------------
    tools: list[str] = Field(default_factory=list)
    pre_hooks: list[str] = Field(default_factory=list)
    post_hooks: list[str] = Field(default_factory=list)
    # --------------------------------------------------
    # Workflow
    # --------------------------------------------------
    workflow: str | None = None
    # --------------------------------------------------
    # Prompt
    # --------------------------------------------------
    prompt: str | None = None
    prompt_limits: str | None = None
    system_messages: list[str] = Field(default_factory=list)
    # --------------------------------------------------
    # Chat
    # --------------------------------------------------
    chat_model: str | None = None
    tool_choice: str | None = None
    parallel_tool_calls: bool | None = None
    streaming: bool = True
    # --------------------------------------------------
    # Cost Recorder
    # --------------------------------------------------
    cost_recorder: str = "local"
    # --------------------------------------------------
    # Observability
    # --------------------------------------------------
    request_logger: str = "local"
    cost_logger: str = "default"
    chat_logger: str = "default"
    tool_logger: str = "default"
    # --------------------------------------------------
    # Finalizer
    # --------------------------------------------------
    finalizers: list[str] = Field(default_factory=lambda: ["subprocess"])
    # --------------------------------------------------
    # Run Context
    # --------------------------------------------------
    organization_id: str = "default"
    user_id: str = "default"
    agent_id: str = "default"
    node_id: str | None = None
    language: str | None = None
    time_zone: str | None = None
    currency: str | None = None
    # --------------------------------------------------
    # GitHub
    # --------------------------------------------------
    github_ignore_cache: bool | None = None
    github_trusted_usernames: list[str] = Field(default_factory=list)
    github_skip_trust_verification: bool | None = None
    # --------------------------------------------------
    # Config
    # --------------------------------------------------
    i18n_catalogs: list[str] = Field(default_factory=list)
    configs: list[str] = Field(default_factory=list)
    config_vars: list[str] = Field(default_factory=list)
    plugins: list[str] = Field(default_factory=list)
    # --------------------------------------------------
    # Logging
    # --------------------------------------------------
    logger_names: list[str] = Field(default_factory=lambda: ["kiari", "kiarina", "kiarina_agi"])
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    # --------------------------------------------------
    # Batch
    # --------------------------------------------------
    batch_handler: str | None = None
    output_text: bool = False
    # --------------------------------------------------
    # Console
    # --------------------------------------------------
    console_handler: str | None = None
    tts: bool = False
    tts_model: str | None = None
    stt: bool = False
    audio_source: str | None = None
    vad_model: str | None = None
    asr_model: str | None = None
    stt_auto_send_after: float | None = None
    editing_mode: Literal["vi", "emacs"] = "vi"
    # --------------------------------------------------
    # Watch
    # --------------------------------------------------
    watchers: list[str] = Field(default_factory=list)
    watch_handler: str | None = None
    watch_max_concurrent: int = 1
    watch_queue_size: int = 1
    watch_queue_put_timeout: float = 300.0
    # --------------------------------------------------
    # Schedule
    # --------------------------------------------------
    interval: str | None = None
    cron: str | None = None
    schedule_handler: str | None = None
    skip_if_no_events: bool = False
    # --------------------------------------------------
    # FastAPI
    # --------------------------------------------------
    fastapi_path: str = "/"
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = Field(default=8000, ge=1, le=65535)
    fastapi_workers: int | None = Field(default=None, ge=1)
    fastapi_handler: str | None = None
    fastapi_authenticator: str | None = None
    # --------------------------------------------------
    # Streamlit
    # --------------------------------------------------
    streamlit_host: str = "127.0.0.1"
    streamlit_port: int = Field(default=8501, ge=1, le=65535)
    streamlit_headless: bool = False
    streamlit_title: str = "Kiari Chat"
    streamlit_icon: str = "🚀"
    streamlit_layout: Literal["centered", "wide"] = "wide"
    streamlit_handler: str | None = None
    streamlit_authenticator: str | None = None

    @field_validator("fastapi_path")
    @classmethod
    def validate_fastapi_path(cls, value: str) -> str:
        if not value.startswith("/"):
            raise ValueError("fastapi_path must start with '/'")

        return value
