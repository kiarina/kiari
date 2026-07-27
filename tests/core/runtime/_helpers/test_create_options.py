import json

import pytest

from kiari.core.profile import RunOptions
from kiari.core.runtime import create_agi_options


def test_create_options() -> None:
    options = create_agi_options(
        RunOptions(
            agent="vanilla",
            max_iterations=1,
            until_end=True,
            until_tool_calls=["hello"],
            until_tool_runs=["hello"],
            tools=["hello"],
            pre_hooks=["hello"],
            post_hooks=["hello"],
            workflow="vanilla",
            prompt="vanilla",
            prompt_limits="token_count_limit=100",
            chat_model="openai",
            tool_choice="auto",
            parallel_tool_calls=True,
            streaming=True,
        )
    )

    assert len(options) > 0
    print(f"Options: {json.dumps(options, indent=2)}")


def test_system_messages() -> None:
    with pytest.raises(ValueError):
        create_agi_options(
            RunOptions(
                prompt="vanilla",
                system_messages=["hello"],
            )
        )

    create_agi_options(
        RunOptions(
            system_messages=["hello"],
        )
    )

    assert True
