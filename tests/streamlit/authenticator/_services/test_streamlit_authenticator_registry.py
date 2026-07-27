from kiari.impl.streamlit_authenticator_impl.browser_session import (
    BrowserSessionAuthenticator,
)
from kiari.impl.streamlit_authenticator_impl.oidc import OIDCAuthenticator
from kiari.streamlit.authenticator import streamlit_authenticator_registry


def test_streamlit_authenticator_registry() -> None:
    browser = streamlit_authenticator_registry.resolve()
    oidc = streamlit_authenticator_registry.resolve("oidc?provider=google")
    assert isinstance(browser, BrowserSessionAuthenticator)
    assert browser.name == "browser-session"
    assert isinstance(oidc, OIDCAuthenticator)
    assert oidc.name == "oidc"
    assert oidc.settings.provider == "google"
