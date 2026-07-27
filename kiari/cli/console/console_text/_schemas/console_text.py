from dataclasses import dataclass, field


@dataclass(frozen=True)
class ConsoleText:
    command_specifier: str | None = None
    command_args: list[str] = field(default_factory=list)
    content: str = ""
