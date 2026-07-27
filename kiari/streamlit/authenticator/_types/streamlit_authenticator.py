from typing import Protocol, runtime_checkable

from kiari.streamlit import StreamlitIdentity

from .streamlit_authenticator_name import StreamlitAuthenticatorName


@runtime_checkable
class StreamlitAuthenticator(Protocol):
    name: StreamlitAuthenticatorName

    def authenticate(self) -> StreamlitIdentity | None: ...

    def logout(self) -> None: ...
