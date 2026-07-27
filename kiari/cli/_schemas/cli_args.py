from dataclasses import dataclass, field

from kiari.core.profile import ProfileName, RunSpec

from .._types.extra_args import ExtraArgs
from .._types.save_mode import SaveMode


@dataclass
class CLIArgs:
    exec_file: str | None = None
    profile_name: ProfileName | None = None
    save_mode: SaveMode | None = None
    run_spec: RunSpec = field(default_factory=dict)
    extra_args: ExtraArgs = field(default_factory=dict)
