from typing import Annotated

from pydantic import StringConstraints

PROFILE_NAME_PATTERN = r"^[a-zA-Z0-9._-]+$"

ProfileName = Annotated[
    str,
    StringConstraints(
        min_length=1,
        pattern=PROFILE_NAME_PATTERN,
    ),
]
