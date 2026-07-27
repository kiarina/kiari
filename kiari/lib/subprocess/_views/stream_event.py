from dataclasses import dataclass
from typing import Literal

from .._types.run_id import RunId


@dataclass
class StreamEvent:
    run_id: RunId
    output: str
    type: Literal["stream"] = "stream"
