from dataclasses import dataclass
from typing import Literal

from .._enums.subprocess_status import SubprocessStatus
from .._types.run_id import RunId


@dataclass
class FinishEvent:
    run_id: RunId
    status: SubprocessStatus
    returncode: int | None
    type: Literal["finish"] = "finish"
