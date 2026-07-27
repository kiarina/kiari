from dataclasses import dataclass
from typing import Literal

from .._types.run_id import RunId


@dataclass
class BackgroundEvent:
    run_id: RunId
    type: Literal["background"] = "background"
