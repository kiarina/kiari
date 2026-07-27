import secrets

import streamlit as st

from kiari.streamlit import StreamlitIdentity
from kiari.streamlit._constants import STREAMLIT_BROWSER_USER_ID_KEY
from kiari.streamlit.authenticator import BaseStreamlitAuthenticator


class BrowserSessionAuthenticator(BaseStreamlitAuthenticator):
    def authenticate(self) -> StreamlitIdentity:
        if STREAMLIT_BROWSER_USER_ID_KEY not in st.session_state:
            st.session_state[STREAMLIT_BROWSER_USER_ID_KEY] = f"browser-{secrets.token_hex(16)}"

        user_id = st.session_state[STREAMLIT_BROWSER_USER_ID_KEY]
        return StreamlitIdentity(
            user_id=user_id,
            display_name="Browser session",
            authenticator_name=str(self.name),
        )
