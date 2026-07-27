from __future__ import annotations

import json
import re
from collections.abc import Iterator
from contextlib import contextmanager, suppress
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import Any, get_args

import pytest
from kiarina.agi.event import ToolMessageEvent
from kiarina.agi.file_info import TextFileInfo
from kiarina.agi.message import ToolCall, ToolMessage
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import BaseTool, run_tool

from kiari.impl.tool_impl.chrome import Chrome
from kiari.impl.tool_impl.chrome._models.chrome import _OPERATIONS
from kiari.impl.tool_impl.chrome._types.action import Action
from kiari.lib.chrome import create_chrome_bridge, settings_manager

pytestmark = [pytest.mark.costly, pytest.mark.timeout(180)]

BUTTON_REF = re.compile(r'- button "Update this profile" \[ref=(s\d+e\d+)\]')
DIALOG_BUTTON_REF = re.compile(r'- button "Open confirmation" \[ref=(s\d+e\d+)\]')
DIALOG_REF = re.compile(r"Dialog ref: (s\d+d\d+)")
LOG_MARKER = "kiari-chrome-integration-clicked"
UPDATED_TEXT = "Updated kiari chrome integration"
DIALOG_ACCEPTED_TEXT = "Confirmed kiari chrome integration"
HTML = f"""<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>kiari Chrome integration</title></head>
  <body>
    <main>
      <h1>Chrome Bridge integration fixture</h1>
      <button id="update" type="button">Update this profile</button>
      <button id="confirm" type="button">Open confirmation</button>
      <p id="status">Ready</p>
    </main>
    <script>
      document.querySelector("#update").addEventListener("click", () => {{
        document.querySelector("#status").textContent = "{UPDATED_TEXT}";
        console.log("{LOG_MARKER}");
      }});
      document.querySelector("#confirm").addEventListener("click", () => {{
        const accepted = window.confirm("Continue kiari Chrome integration?");
        document.querySelector("#status").textContent = accepted
          ? "{DIALOG_ACCEPTED_TEXT}"
          : "Cancelled kiari chrome integration";
      }});
    </script>
  </body>
</html>
""".encode()


class FixtureHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(HTML)))
        self.end_headers()
        self.wfile.write(HTML)

    def log_message(self, format: str, *args: object) -> None:
        return


@contextmanager
def serve_fixture() -> Iterator[str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}/fixture"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


async def run_chrome(
    tool: BaseTool,
    run_context: RunContext,
    args: dict[str, Any],
) -> ToolMessage:
    events = [
        event
        async for event in run_tool(
            ToolCall(name="chrome", args=args),
            tool_options={"tools": [tool]},
            run_context=run_context,
        )
    ]
    messages = [event.message for event in events if isinstance(event, ToolMessageEvent)]
    assert len(messages) == 1
    message = messages[0]
    assert not message.failed, message.contents[0].text
    return message


def result_text(message: ToolMessage) -> str:
    assert len(message.contents) == 1
    content = message.contents[0]
    parts = [content.text] if content.text is not None else []
    parts.extend(file.raw_text for file in content.files if isinstance(file, TextFileInfo))
    return "\n\n".join(parts)


async def close_owned_tab(tab_id: int, browser_id: str) -> None:
    with suppress(Exception):
        bridge = create_chrome_bridge()
        async with bridge.session(
            wait_timeout=settings_manager.settings.session_wait_timeout
        ) as session:
            await session.browser_tab_close(tab_id=tab_id, browser_id=browser_id)


async def close_owned_urls(urls: set[str], browser_id: str) -> None:
    with suppress(Exception):
        bridge = create_chrome_bridge()
        async with bridge.session(
            wait_timeout=settings_manager.settings.session_wait_timeout
        ) as session:
            tabs = await session.browser_tabs(browser_id=browser_id)
            for tab in tabs:
                if tab.url in urls:
                    await session.browser_tab_close(tab_id=tab.id, browser_id=browser_id)


@pytest.fixture
def chrome_tool() -> BaseTool:
    tool = Chrome()
    tool.name = "chrome"
    return tool


async def test_real_sdk_and_extension_contract(
    chrome_tool: BaseTool,
    run_context: RunContext,
) -> None:
    assert set(get_args(Action)) == set(_OPERATIONS)

    fixture_tab_id: int | None = None
    browser_id: str | None = None
    with serve_fixture() as fixture_url:
        instances = json.loads(
            result_text(await run_chrome(chrome_tool, run_context, {"action": "instances"}))
        )
        assert instances, "Chrome Bridge extension is connected, but reported no browser"
        browser_id = instances[0]["browser_id"]

        initial_tabs = json.loads(
            result_text(
                await run_chrome(
                    chrome_tool,
                    run_context,
                    {"action": "tabs", "browser_id": browser_id},
                )
            )
        )
        initial_tab_ids = {tab["id"] for tab in initial_tabs}
        active_tab_ids = {tab["id"] for tab in initial_tabs if tab["active"]}

        try:
            opened = json.loads(
                result_text(
                    await run_chrome(
                        chrome_tool,
                        run_context,
                        {
                            "action": "tab_open",
                            "url": fixture_url,
                            "active": False,
                            "browser_id": browser_id,
                        },
                    )
                )
            )
            fixture_tab_id = opened["id"]
            assert not opened["active"]

            selected = json.loads(
                result_text(
                    await run_chrome(
                        chrome_tool,
                        run_context,
                        {
                            "action": "tab_select",
                            "tab_id": fixture_tab_id,
                            "browser_id": browser_id,
                        },
                    )
                )
            )
            assert selected["targeted"]
            assert not selected["active"]

            ready = result_text(
                await run_chrome(
                    chrome_tool,
                    run_context,
                    {
                        "action": "wait_for",
                        "text": "Ready",
                        "browser_id": browser_id,
                    },
                )
            )
            assert f"URL: {fixture_url}" in ready

            snapshot = result_text(
                await run_chrome(
                    chrome_tool,
                    run_context,
                    {"action": "snapshot", "browser_id": browser_id},
                )
            )
            match = BUTTON_REF.search(snapshot)
            assert match is not None
            assert f"URL: {fixture_url}" in snapshot
            assert "Title: kiari Chrome integration" in snapshot

            clicked = result_text(
                await run_chrome(
                    chrome_tool,
                    run_context,
                    {
                        "action": "click",
                        "element": "Update this profile button",
                        "ref": match.group(1),
                        "browser_id": browser_id,
                    },
                )
            )
            assert UPDATED_TEXT in clicked
            dialog_button_match = DIALOG_BUTTON_REF.search(clicked)
            assert dialog_button_match is not None

            dialog = result_text(
                await run_chrome(
                    chrome_tool,
                    run_context,
                    {
                        "action": "click",
                        "element": "Open confirmation button",
                        "ref": dialog_button_match.group(1),
                        "browser_id": browser_id,
                    },
                )
            )
            assert "Browser dialog: confirm" in dialog
            assert "Message: Continue kiari Chrome integration?" in dialog
            dialog_ref_match = DIALOG_REF.search(dialog)
            assert dialog_ref_match is not None

            continued = result_text(
                await run_chrome(
                    chrome_tool,
                    run_context,
                    {
                        "action": "dialog_respond",
                        "dialog_ref": dialog_ref_match.group(1),
                        "dialog_action": "accept",
                        "browser_id": browser_id,
                    },
                )
            )
            assert DIALOG_ACCEPTED_TEXT in continued

            screenshot = await run_chrome(
                chrome_tool,
                run_context,
                {"action": "screenshot", "browser_id": browser_id},
            )
            content = screenshot.contents[0]
            assert "image/png" in (content.text or "")
            assert len(content.files) == 1
            assert content.files[0].type == "image"

            logs = result_text(
                await run_chrome(
                    chrome_tool,
                    run_context,
                    {"action": "console_logs", "browser_id": browser_id},
                )
            )
            assert any(LOG_MARKER in json.loads(line)["message"] for line in logs.splitlines())

            final_tabs = json.loads(
                result_text(
                    await run_chrome(
                        chrome_tool,
                        run_context,
                        {"action": "tabs", "browser_id": browser_id},
                    )
                )
            )
            assert {tab["id"] for tab in final_tabs if tab["active"]} == active_tab_ids

            closed = json.loads(
                result_text(
                    await run_chrome(
                        chrome_tool,
                        run_context,
                        {
                            "action": "tab_close",
                            "tab_id": fixture_tab_id,
                            "browser_id": browser_id,
                        },
                    )
                )
            )
            assert closed["closed"]
            fixture_tab_id = None

            opened_without_target = json.loads(
                result_text(
                    await run_chrome(
                        chrome_tool,
                        run_context,
                        {
                            "action": "tab_open",
                            "url": fixture_url,
                            "active": False,
                            "browser_id": browser_id,
                        },
                    )
                )
            )
            fixture_tab_id = opened_without_target["id"]
            assert opened_without_target["targeted"]
            assert not opened_without_target["active"]
            await run_chrome(
                chrome_tool,
                run_context,
                {
                    "action": "tab_close",
                    "tab_id": fixture_tab_id,
                    "browser_id": browser_id,
                },
            )
            fixture_tab_id = None

            navigated_without_target = result_text(
                await run_chrome(
                    chrome_tool,
                    run_context,
                    {
                        "action": "navigate",
                        "url": fixture_url,
                        "browser_id": browser_id,
                    },
                )
            )
            assert f"URL: {fixture_url}" in navigated_without_target
            bootstrap_tabs = json.loads(
                result_text(
                    await run_chrome(
                        chrome_tool,
                        run_context,
                        {"action": "tabs", "browser_id": browser_id},
                    )
                )
            )
            bootstrap_targets = [
                tab
                for tab in bootstrap_tabs
                if tab["targeted"] and tab["id"] not in initial_tab_ids
            ]
            assert len(bootstrap_targets) == 1
            fixture_tab_id = bootstrap_targets[0]["id"]
            assert not bootstrap_targets[0]["active"]
            assert {tab["id"] for tab in bootstrap_tabs if tab["active"]} == active_tab_ids
            await run_chrome(
                chrome_tool,
                run_context,
                {
                    "action": "tab_close",
                    "tab_id": fixture_tab_id,
                    "browser_id": browser_id,
                },
            )
            fixture_tab_id = None
        finally:
            if fixture_tab_id is not None and browser_id is not None:
                await close_owned_tab(fixture_tab_id, browser_id)
            if browser_id is not None:
                await close_owned_urls({fixture_url}, browser_id)
