from pydantic import BaseModel


class StreamlitIdentity(BaseModel):
    user_id: str
    display_name: str
    authenticator_name: str
