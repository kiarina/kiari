from typing import Literal

from pydantic import BaseModel, Field

from .._types.action import Action


class ChromeSchema(BaseModel):
    """
    Operate tabs in connected Chrome profiles through Chrome Bridge.

    Use instances/tabs/tab_select before page actions. snapshot returns accessibility
    refs for element actions or a dominant browser dialog for dialog_respond.
    A ref is valid only for its browser, target tab, document, and latest snapshot.
    Each action uses a separate exclusive session, so another client may invalidate
    target or ref state between actions; take a fresh snapshot when state may have changed.
    """

    action: Action = Field(
        description=(
            "Chrome action and its main arguments:\n"
            "- instances: list browsers\n"
            "- tabs: list tabs\n"
            "- tab_open: optional url, active\n"
            "- tab_close, tab_select, tab_activate: tab_id\n"
            "- snapshot, screenshot, console_logs: no action-specific arguments\n"
            "- dialog_respond: dialog_ref, dialog_action; optional prompt_text\n"
            "- click, hover: element, ref; optional video_filename\n"
            "- drag: start_element, start_ref, end_element, end_ref; optional video_filename\n"
            "- upload_file: element, ref, paths; optional video_filename\n"
            "- type: element, ref, text; optional submit, video_filename\n"
            "- select_option: element, ref, values; optional video_filename\n"
            "- press_key: key; optional video_filename\n"
            "- navigate: url; optional video_filename\n"
            "- go_back, go_forward: optional video_filename\n"
            "- wait: time; optional video_filename\n"
            "- wait_for: text; optional state, timeout, video_filename\n"
            "- download_file: element, ref; optional timeout\n"
            "- record_video: filename, duration\n"
            "All actions except instances optionally accept browser_id."
        )
    )
    browser_id: str | None = Field(
        default=None,
        description=(
            "Browser ID from instances. Optional with one connected browser and required "
            "with multiple browsers. Used by every action except instances."
        ),
    )
    tab_id: int | None = Field(
        default=None,
        description="Tab ID from tabs. Required for tab_close, tab_select, and tab_activate.",
    )
    url: str | None = Field(
        default=None,
        description=(
            "URL for tab_open or navigate. tab_open defaults to about:blank and targets "
            "the new tab when no target exists. navigate requires an HTTP(S) URL and "
            "creates an inactive target tab when needed."
        ),
    )
    active: bool = Field(default=True, description="Whether tab_open activates the new tab.")
    element: str | None = Field(
        default=None,
        description=(
            "Human-readable element description from the latest snapshot. Required for "
            "click, hover, upload_file, type, select_option, and download_file."
        ),
    )
    ref: str | None = Field(
        default=None,
        description=(
            "Strict ref from the latest snapshot. Required for click, hover, upload_file, "
            "type, select_option, and download_file."
        ),
    )
    text: str | None = Field(
        default=None,
        description="Text for type (required but may be empty) or wait_for (non-empty).",
    )
    submit: bool = Field(default=False, description="Send Enter after type.")
    values: list[str] = Field(
        default_factory=list, description="One or more exact values for select_option."
    )
    paths: list[str] = Field(
        default_factory=list,
        description="One to twenty absolute local paths for upload_file.",
    )
    start_element: str | None = Field(default=None, description="Source element for drag.")
    start_ref: str | None = Field(default=None, description="Source ref for drag.")
    end_element: str | None = Field(default=None, description="Destination element for drag.")
    end_ref: str | None = Field(default=None, description="Destination ref for drag.")
    key: str | None = Field(default=None, description="Key or key chord for press_key.")
    time: float | None = Field(default=None, description="Seconds from 0 through 10 for wait.")
    state: Literal["visible", "hidden"] = Field(
        default="visible", description="Desired text state for wait_for."
    )
    timeout: float = Field(
        default=10, description="Timeout in seconds for wait_for or download_file."
    )
    filename: str | None = Field(default=None, description="Safe .webm filename for record_video.")
    duration: float | None = Field(
        default=None, description="Duration in seconds for record_video."
    )
    video_filename: str | None = Field(
        default=None,
        description=(
            "Optional safe .webm filename to record supported page actions around the operation."
        ),
    )
    dialog_ref: str | None = Field(
        default=None,
        description=(
            "Exact dialog ref from a browser-dialog page state. Required for dialog_respond."
        ),
    )
    dialog_action: Literal["accept", "dismiss"] | None = Field(
        default=None,
        description=(
            "Response for dialog_respond. For beforeunload, accept leaves and dismiss stays."
        ),
    )
    prompt_text: str | None = Field(
        default=None,
        description=(
            "Text for accepting a prompt in dialog_respond; omit for other dialog responses."
        ),
    )
