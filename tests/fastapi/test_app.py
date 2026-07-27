import json

import httpx

import kiari.fastapi.app as app_module
from kiari.core.profile import RunOptions
from kiari.fastapi import FastAPIStartupOptions, create_app


async def _noop(*args, **kwargs) -> None:
    pass


async def test_fastapi_health_and_ndjson(monkeypatch, setup_run_context) -> None:
    monkeypatch.setattr(app_module, "setup_runtime", _noop)
    monkeypatch.setattr(app_module, "run_finalizers", _noop)
    app = create_app(
        FastAPIStartupOptions(
            profile_name="test",
            run_options=RunOptions(
                chat_model="mock",
                cost_recorder="null",
                finalizers=[],
                no_load=True,
                fastapi_path="/agent",
            ),
        )
    )

    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            health_response = await client.get("/health")
            response = await client.post("/agent", json={"text": "hello"})

    assert health_response.status_code == 200
    assert health_response.json() == {"status": "ok"}
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/x-ndjson")
    events = [json.loads(line) for line in response.text.splitlines()]
    assert events[-1]["type"] == "ai_message"


async def test_fastapi_validates_before_streaming(monkeypatch, setup_run_context) -> None:
    monkeypatch.setattr(app_module, "setup_runtime", _noop)
    monkeypatch.setattr(app_module, "run_finalizers", _noop)
    app = create_app(
        FastAPIStartupOptions(
            profile_name="test",
            run_options=RunOptions(
                chat_model="mock",
                cost_recorder="null",
                finalizers=[],
                no_load=True,
                fastapi_authenticator="bearer?api_key=secret",
            ),
        )
    )

    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            empty_response = await client.post("/", json={})
            unauthorized_response = await client.post("/", json={"text": "hello"})
            config_response = await client.post(
                "/",
                json={"text": "hello", "config": {"log_level": "DEBUG"}},
                headers={"Authorization": "Bearer secret"},
            )
            event_response = await client.post(
                "/",
                json={"events": [{"type": "invalid"}]},
                headers={"Authorization": "Bearer secret"},
            )

    assert empty_response.status_code == 422
    assert unauthorized_response.status_code == 401
    assert config_response.status_code == 422
    assert event_response.status_code == 422


async def test_agent_error_is_streamed(monkeypatch, setup_run_context) -> None:
    monkeypatch.setattr(app_module, "setup_runtime", _noop)
    monkeypatch.setattr(app_module, "run_finalizers", _noop)
    app = create_app(
        FastAPIStartupOptions(
            profile_name="test",
            run_options=RunOptions(
                chat_model="mock",
                cost_recorder="null",
                finalizers=[],
                no_load=True,
            ),
        )
    )

    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/",
                json={"text": "hello", "config": {"agent": "missing-agent"}},
            )

    event = json.loads(response.text)
    assert response.status_code == 200
    assert event["type"] == "custom"
    assert event["payload"]["type"] == "error"
