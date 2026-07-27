from kiari.fastapi.authenticator import BaseAuthenticator, authenticator_registry
from kiari.impl.authenticator_impl.bearer import BearerAuthenticator


def test_authenticator_registry() -> None:
    assert isinstance(authenticator_registry.resolve(), BaseAuthenticator)

    bearer = authenticator_registry.resolve("bearer?api_key=secret")
    assert isinstance(bearer, BearerAuthenticator)
    assert bearer.settings.api_key is not None
    assert bearer.settings.api_key.get_secret_value() == "secret"
