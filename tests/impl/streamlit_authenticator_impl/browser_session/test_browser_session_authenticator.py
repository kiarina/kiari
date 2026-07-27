from types import SimpleNamespace

from kiari.impl.streamlit_authenticator_impl.browser_session import (
    BrowserSessionAuthenticator,
)
from kiari.impl.streamlit_authenticator_impl.browser_session._models import (
    browser_session_authenticator as module,
)


def test_browser_session_identity_is_stable(monkeypatch) -> None:
    monkeypatch.setattr(module, "st", SimpleNamespace(session_state={}))
    authenticator = BrowserSessionAuthenticator()
    authenticator.name = "browser-session"
    first = authenticator.authenticate()
    second = authenticator.authenticate()
    assert first == second
    assert first.user_id.startswith("browser-")
