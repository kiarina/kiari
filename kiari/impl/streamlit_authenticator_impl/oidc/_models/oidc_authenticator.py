import hashlib
from typing import Any

import streamlit as st

from kiari.streamlit import StreamlitIdentity
from kiari.streamlit.authenticator import BaseStreamlitAuthenticator

from .._settings import OIDCAuthenticatorSettings, settings_manager


class OIDCAuthenticator(BaseStreamlitAuthenticator):
    def __init__(
        self,
        settings: OIDCAuthenticatorSettings | None = None,
        **kwargs: Any,
    ) -> None:
        base_settings = settings or settings_manager.settings
        self.settings = OIDCAuthenticatorSettings.model_validate(
            {**base_settings.model_dump(), **kwargs}
        )
        self._name = None

    def authenticate(self) -> StreamlitIdentity | None:
        if not st.user.is_logged_in:
            args = [self.settings.provider] if self.settings.provider else []
            st.button("Log in", on_click=st.login, args=args)
            return None

        subject = st.user.get("sub")
        if not subject:
            raise RuntimeError("OIDC identity does not contain a 'sub' claim")

        issuer = st.user.get("iss") or self.settings.provider or "default"
        digest = hashlib.sha256(f"{issuer}\0{subject}".encode()).hexdigest()
        display_name = st.user.get(self.settings.display_name_claim) or st.user.get("email")
        return StreamlitIdentity(
            user_id=f"oidc-{digest}",
            display_name=str(display_name or subject),
            authenticator_name=str(self.name),
        )

    def logout(self) -> None:
        st.logout()
