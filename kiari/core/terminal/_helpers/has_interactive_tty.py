import sys


def has_interactive_tty() -> bool:
    return any(
        stream is not None and stream.isatty() for stream in (sys.stdin, sys.stdout, sys.stderr)
    )
