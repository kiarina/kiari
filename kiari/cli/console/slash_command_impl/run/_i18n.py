from kiarina.i18n import I18n


class RunSlashCommandI18n(I18n, scope="kiari.cli.console.slash_command_impl.run"):
    description: str = (
        "Run the agent with optional one-shot condition overrides.\n\n"
        "  [cyan]/run[/cyan]                                      "
        "Run the agent\n"
        "  [cyan]/run[/cyan] [yellow]<n>[/yellow]                  "
        "Override max_iterations for this run\n"
        "  [cyan]/run[/cyan] [yellow]--until-end[/yellow]          "
        "Continue until conversation end for this run\n"
        "  [cyan]/run[/cyan] [yellow]--until-tool-call <tool>[/yellow]   "
        "Stop after tool call request [dim](repeatable)[/dim]\n"
        "  [cyan]/run[/cyan] [yellow]--until-tool-run <tool>[/yellow]    "
        "Stop after tool run [dim](repeatable)[/dim]\n\n"
        "  [dim]Example:[/dim]\n"
        "    [dim]/run 10 --until-end --until-tool-call hello "
        "--until-tool-call world --until-tool-run foo[/dim]"
    )
    invalid_args: str = "Invalid /run arguments: {args}"
    missing_value: str = "Missing value for {option}"
    run_started: str = "Run agent"
    set_max_iterations: str = "max_iterations: {max_iterations}"
    set_until_end: str = "until_end: yes"
    set_until_tool_calls: str = "until_tool_calls: {tool_names}"
    set_until_tool_runs: str = "until_tool_runs: {tool_names}"
