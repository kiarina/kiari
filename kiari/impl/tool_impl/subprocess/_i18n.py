from kiarina.i18n import I18n


class SubprocessI18n(I18n, scope="kiari.impl.tool_impl.subprocess"):
    run_id_not_found_error: str = "Error: Run ID '{run_id}' does not exist"
    already_completed_error: str = (
        "Error: Process with run ID '{run_id}' has already completed (status: {status})"
    )
    cancel_error: str = "Error: An error occurred while canceling the process: {error}"

    # cancel action
    immediate_forced_termination: str = "Immediate forced termination"
    graceful_shutdown: str = "Graceful shutdown (waiting {timeout} seconds)"
    cancel_result: str = (
        "Run ID: {run_id}\n"
        "Command: {argv}\n"
        "Shutdown method: {shutdown_method}\n"
        "Execution status: {status}\n"
        "Exit code: {returncode}\n\n"
        "Process cancellation completed."
    )

    # get_output action
    get_output_result: str = (
        "Run ID: {run_id}\n"
        "Command: {argv}\n"
        "Execution status: {status}\n"
        "Execution time: {duration:.2f} seconds\n"
        "Exit code: {returncode}\n"
        "Completed: {completed}\n\n"
        "Output:\n"
    )
    process_completed_successfully: str = "Process completed successfully."
    process_cancelled: str = "Process was cancelled."
    process_failed: str = "Process failed (exit code: {returncode})."
    process_running: str = "Process is running."
    yes: str = "Yes"
    no: str = "No"

    # get_list action
    processes_found: str = "Found {count} tracked process(es).\n\n"
    process_info: str = (
        "Run ID: {run_id}\n"
        "Command: {argv}\n"
        "Execution time: {duration:.2f} seconds\n"
        "Execution status: {status}\n"
        "Exit code: {returncode}\n\n"
    )
    no_processes: str = "No tracked processes found."

    # run action
    run_result: str = (
        "Run ID: {run_id}\nCommand: {argv}\nWait time: {wait_time} seconds\n\nResult:\n"
    )
    run_execution_completed: str = "Execution completed."
    run_running_background: str = (
        "Process is running in the background.\n"
        "Use subprocess tool with action=get_output, run_id={run_id} to check the output."
    )

    # run_background action
    run_background_result: str = (
        "Run ID: {run_id}\n"
        "Command: {argv}\n\n"
        "Result:\n"
        "Process started running in the background.\n"
        "Use subprocess tool with action=get_output, run_id={run_id} to check the output."
    )
