from typing import Literal

from pydantic import BaseModel

from kiari.core.profile import ProfileName, RunOptions


class StreamlitStartupOptions(BaseModel):
    schema_version: Literal[1] = 1
    profile_name: ProfileName
    run_options: RunOptions
