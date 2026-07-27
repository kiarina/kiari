from pydantic import BaseModel

from kiari.core.profile import ProfileName, RunOptions


class ExtensionCommandContext(BaseModel):
    profile_name: ProfileName
    run_options: RunOptions
