import sys
from typing import TypedDict

from prompt_toolkit.input.base import Input
from prompt_toolkit.input.defaults import create_input
from prompt_toolkit.output.base import Output
from prompt_toolkit.output.defaults import create_output


class PromptToolkitIO(TypedDict):
    input: Input
    output: Output


def create_prompt_toolkit_io() -> PromptToolkitIO:
    return {
        "input": create_input(always_prefer_tty=True),
        "output": create_output(stdout=sys.stderr),
    }
