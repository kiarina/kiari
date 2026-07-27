from typing import Any

from kiari.streamlit import StreamlitIdentity

from .._types.streamlit_authenticator import StreamlitAuthenticator
from .._types.streamlit_authenticator_name import StreamlitAuthenticatorName


class BaseStreamlitAuthenticator(StreamlitAuthenticator):
    def __init__(self, **kwargs: Any) -> None:
        self.init_kwargs = kwargs
        self._name: StreamlitAuthenticatorName | None = None

    @property
    def name(self) -> StreamlitAuthenticatorName:
        if self._name is None:  # pragma: no cover
            raise AssertionError("StreamlitAuthenticator name not set")
        return self._name

    @name.setter
    def name(self, value: StreamlitAuthenticatorName) -> None:
        self._name = value

    def authenticate(self) -> StreamlitIdentity | None:
        raise NotImplementedError

    def logout(self) -> None:
        pass
