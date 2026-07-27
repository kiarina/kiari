import pytest
from fastapi import HTTPException
from kiarina.agi.event import HumanMessageEvent

from kiari.core.profile import RunOptions
from kiari.fastapi import RequestBody
from kiari.fastapi.fastapi_handler import BaseFastAPIHandler, FastAPIRequest


class ExampleFastAPIHandler(BaseFastAPIHandler):
    pass


async def test_create_session_with_request_overrides(setup_run_context) -> None:
    handler = ExampleFastAPIHandler(
        "test",
        RunOptions(
            chat_model="mock",
            cost_recorder="null",
            no_load=True,
        ),
    )
    previous_event = HumanMessageEvent.create("previous")
    request = FastAPIRequest(
        body=RequestBody(
            text="hello",
            events=[previous_event.model_dump(mode="json")],
            config={"max_iterations": 2},
            run_kwargs={"example": "value"},
        ),
        headers={"x-test": "value"},
    )

    async with handler.handle_request(request) as session:
        assert session.run_options.max_iterations == 2
        assert session.run_kwargs == {"example": "value"}
        assert session.request_headers == {"x-test": "value"}
        assert len(session.history.events) == 2
        assert session.as_run_agent_kwargs()["example"] == "value"


@pytest.mark.parametrize(
    ("body", "message"),
    [
        (
            RequestBody(text="hello", config={"log_level": "DEBUG"}),
            "cannot be overridden",
        ),
        (
            RequestBody(text="hello", run_kwargs={"history": {}}),
            "reserved fields",
        ),
    ],
)
async def test_reject_invalid_request_configuration(
    body: RequestBody,
    message: str,
    setup_run_context,
) -> None:
    handler = ExampleFastAPIHandler(
        "test",
        RunOptions(cost_recorder="null", no_load=True),
    )

    with pytest.raises(HTTPException, match=message) as exc_info:
        async with handler.handle_request(FastAPIRequest(body=body)):
            pass

    assert exc_info.value.status_code == 422
