import pytest
from fastapi import HTTPException

from kiari.core.profile import RunOptions
from kiari.fastapi import RequestBody
from kiari.fastapi.fastapi_handler import FastAPIRequest
from kiari.impl.authenticator_impl.bearer import BearerAuthenticator


async def test_bearer_authenticator_success(setup_run_context) -> None:
    authenticator = BearerAuthenticator(api_key="secret")
    run_context = await authenticator.authenticate(
        FastAPIRequest(
            body=RequestBody(text="hello"),
            headers={"authorization": "Bearer secret"},
        ),
        RunOptions(),
    )

    assert run_context.organization_id == "kiari"


@pytest.mark.parametrize(
    ("headers", "message"),
    [
        ({}, "Authorization header is required"),
        ({"authorization": "Basic secret"}, "Invalid authorization header format"),
        ({"authorization": "Bearer wrong"}, "Invalid API key"),
    ],
)
async def test_bearer_authenticator_rejects_invalid_header(
    headers: dict[str, str],
    message: str,
) -> None:
    authenticator = BearerAuthenticator(api_key="secret")

    with pytest.raises(HTTPException, match=message) as exc_info:
        await authenticator.authenticate(
            FastAPIRequest(body=RequestBody(text="hello"), headers=headers),
            RunOptions(),
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}


async def test_bearer_authenticator_requires_api_key() -> None:
    authenticator = BearerAuthenticator()

    with pytest.raises(RuntimeError, match="API key is not configured"):
        await authenticator.authenticate(
            FastAPIRequest(body=RequestBody(text="hello")),
            RunOptions(),
        )
