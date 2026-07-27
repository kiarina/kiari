from types import SimpleNamespace

import pytest

from kiari.impl.streamlit_authenticator_impl.oidc import OIDCAuthenticator
from kiari.impl.streamlit_authenticator_impl.oidc._models import oidc_authenticator as module


class User(dict):
    is_logged_in = True


def test_oidc_identity_is_stable_and_provider_scoped(monkeypatch) -> None:
    fake_st = SimpleNamespace(user=User(sub="123", name="Alice"), logout=lambda: None)
    monkeypatch.setattr(module, "st", fake_st)
    authenticator = OIDCAuthenticator(provider="google")
    authenticator.name = "oidc"
    identity = authenticator.authenticate()
    assert identity is not None
    assert identity.user_id.startswith("oidc-")
    assert identity.display_name == "Alice"
    assert identity == authenticator.authenticate()


def test_oidc_requires_subject(monkeypatch) -> None:
    monkeypatch.setattr(module, "st", SimpleNamespace(user=User(name="Alice")))
    authenticator = OIDCAuthenticator(provider="google")
    authenticator.name = "oidc"
    with pytest.raises(RuntimeError, match="sub"):
        authenticator.authenticate()
