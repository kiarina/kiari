from pydantic import BaseModel, Field

from .._types.action import Action


class SubprocessSchema(BaseModel):
    """
    Execute a program by directly specifying its argument vector (argv).

    The argv is executed directly without an intermediate shell, so shell
    features (pipes, redirections, globbing, environment-variable expansion,
    `&&`/`||`, etc.) are NOT available. To use them, invoke a shell explicitly,
    e.g. argv=["bash", "-lc", "ls *.py | wc -l"]. To run Python code, use
    argv=["python", "-c", "..."] (or ["python", "-"] together with input_data).

    Supports the following actions:
    - run: Execute a program and wait for it in the foreground
      Required arguments: argv
      Optional arguments: cwd, env, input_data, wait_time
    - run_background: Execute a program in the background (do not wait)
      Required arguments: argv
      Optional arguments: cwd, env, input_data
    - get_output: Get the output of a running or completed process
      Required arguments: run_id
      Optional arguments: start_line, end_line
    - get_list: Get a list of running processes
      Required arguments: none
    - cancel: Cancel a running process
      Required arguments: run_id
      Optional arguments: graceful_shutdown_timeout
    """

    action: Action = Field(
        description=(
            "Action to execute\n"
            '- "run": Execute a program and wait in the foreground '
            "(Required arguments: argv)\n"
            '- "run_background": Execute a program in the background '
            "(Required arguments: argv)\n"
            '- "get_output": Get the output of a running or completed process '
            "(Required arguments: run_id)\n"
            '- "get_list": Get a list of running processes '
            "(Required arguments: none)\n"
            '- "cancel": Cancel a running process (Required arguments: run_id)'
        ),
    )

    # --------------------------------------------------
    # run / run_background action arguments
    # --------------------------------------------------

    argv: list[str] = Field(
        default_factory=list,
        description=(
            "Argument vector to execute, as a list: the program followed by its "
            'arguments (e.g. ["git", "--no-pager", "status"]). '
            "(For run, run_background actions)\n\n"
            "The program is executed directly WITHOUT a shell, so pipes, "
            "redirections, globbing, variable expansion and `&&`/`||` do NOT work. "
            "To use shell features, run a shell explicitly, e.g. "
            '["bash", "-lc", "ls *.py | wc -l"]. To run Python code, use '
            '["python", "-c", "..."].\n\n'
            "Always pass the --no-pager flag (or set env PAGER=cat) for git, "
            "systemctl, kubectl, etc. so the process does not block on a pager. "
            "Prefer targeted commands over broad scans to avoid excessive output."
        ),
    )

    cwd: str | None = Field(
        default=None,
        description=(
            "Working directory to run the program in. If None, the current "
            "directory is used. (For run, run_background actions)"
        ),
    )

    env: dict[str, str] | None = Field(
        default=None,
        description=(
            "Extra environment variables, merged on top of the current "
            "environment (existing variables such as PATH are preserved). "
            "(For run, run_background actions)"
        ),
    )

    input_data: str | None = Field(
        default=None,
        description=(
            "Data written to the process's standard input. If None, stdin is "
            "closed immediately (EOF). (For run, run_background actions)"
        ),
    )

    # --------------------------------------------------
    # Common options (for run)
    # --------------------------------------------------

    wait_time: int | None = Field(
        default=None,
        description=(
            "Wait time in seconds for foreground execution. After this time, "
            "execution will move to the background. If None, the default value "
            "(60 seconds) will be used. (For run action)"
        ),
    )

    # --------------------------------------------------
    # get_output action arguments
    # --------------------------------------------------

    run_id: str = Field(
        default="",
        description=("ID of the execution to get output from. (For get_output, cancel actions)"),
    )

    start_line: int = Field(
        default=1,
        description=(
            "Start line of the display range (starting from 1, negative numbers "
            "specify from the end, -1 is the last line). (For get_output action)"
        ),
    )

    end_line: int = Field(
        default=-1,
        description=(
            "End line of the display range (starting from 1, negative numbers "
            "specify from the end, -1 is the last line). (For get_output action)"
        ),
    )

    # --------------------------------------------------
    # cancel action arguments
    # --------------------------------------------------

    graceful_shutdown_timeout: float = Field(
        default=3.0,
        description=(
            "Maximum seconds to wait for graceful shutdown. First sends a graceful "
            "shutdown signal (Windows: CTRL_BREAK_EVENT, Unix: SIGTERM), and if the "
            "process doesn't terminate within this time, forces termination "
            "(SIGKILL equivalent). If 0 is specified, forces immediate termination. "
            "(For cancel action)"
        ),
    )
