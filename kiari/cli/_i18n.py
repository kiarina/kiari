from kiarina.i18n import I18n


class CLII18n(I18n, scope="kiari.cli"):
    # --------------------------------------------------
    # History Repository
    # --------------------------------------------------
    history_repository_help: str = (
        "History repository name or config string. Example: 'null', 'in_memory', "
        "or 'local?file_name=history.json'."
    )
    stateless_help: str = "If set, the history will not be loaded or saved during the run."
    no_load_help: str = "If set, the history will not be loaded at the start of the run."
    no_save_help: str = "If set, the history will not be saved at the end of the run."
    allow_active_missing_tools_help: str = (
        "If set, keep loaded active tool infos active even when the tool is missing."
    )
    # --------------------------------------------------
    # History
    # --------------------------------------------------
    events_help: str = (
        "Event to seed into history. Repeatable. Example: 'Hello', "
        '\'{"text": "Hello", "files": ["/path/to/file.txt"]}\', or '
        '\'["ai", "Hello"]\'.'
    )
    file_infos_help: str = (
        "File info input to seed into history. Repeatable. Plain strings are "
        "interpreted as URI or file path patterns; non-URI strings are expanded "
        "with kiari file resolution and may produce multiple files. JSON input "
        "is treated as a single FileInfoSpec and is not pattern-expanded. Examples: "
        "'/path/to/file.txt', 'src/**/*.py', '@kiarina/kiari/README.md', or "
        '\'{"uri_or_file_path": "/path/to/file.txt", "group": "dev"}\'.'
    )
    tool_infos_help: str = (
        "Tool info to seed into history. Repeatable. Format: "
        "'{tool_name}' or '{state}:{tool_name}' or '{tool_info_json}'. "
        "'Example: 'run' or 'inactive:run' or "
        '\'{"name":"hello","description":"Says hello"}\'.'
    )
    default_tool_state_help: str = "Default state for tool infos derived from AGI tools."
    # --------------------------------------------------
    # Agent
    # --------------------------------------------------
    agent_help: str = (
        "Agent name or config string to run. Example: 'vanilla' or "
        "'vanilla?key1=value1&key2=value2'."
    )
    file_limits_help: str = (
        "File limits config string used to prepare files before agent execution. "
        "Example: 'token_count_limit=4096&file_size_limit=20000000'."
    )
    max_iterations_help: str = "Maximum number of agent iterations before stopping."
    until_end_help: str = "Continue agent execution until it reaches its natural end condition."
    until_tool_calls_help: str = (
        "Stop after the specified tool is requested by the model. Repeatable."
    )
    until_tool_runs_help: str = "Stop after the specified tool has actually run. Repeatable."
    # --------------------------------------------------
    # Tool
    # --------------------------------------------------
    tools_help: str = (
        "Tool to make available to the AGI run. Repeatable. Example: 'run' or "
        "'run?key1=value1&key2=value2'."
    )
    pre_hooks_help: str = (
        "Pre-hook to apply before tool execution. Repeatable. Example: 'confirm', "
        "'confirm?message=Proceed', or 'confirm@run,finish'."
    )
    post_hooks_help: str = (
        "Post-hook to apply after tool execution. Repeatable. Example: 'notify', "
        "'notify?channel=dev', or 'notify@run,finish'."
    )
    # --------------------------------------------------
    # Workflow
    # --------------------------------------------------
    workflow_help: str = (
        "Workflow name or config string to run. Example: 'vanilla' or "
        "'vanilla?key1=value1&key2=value2'."
    )
    # --------------------------------------------------
    # Prompt
    # --------------------------------------------------
    prompt_help: str = (
        "Prompt name or config string to use. Example: 'vanilla' or "
        "'vanilla?key1=value1&key2=value2'."
    )
    prompt_limits_help: str = (
        "Prompt limits config string used to constrain prompt building. Example: "
        "'token_count_limit=4096,file_size_limit=20000000'."
    )
    system_messages_help: str = (
        "System message to prepend to the prompt. Repeatable. Cannot be used "
        "together with --prompt."
    )
    # --------------------------------------------------
    # Chat
    # --------------------------------------------------
    chat_model_help: str = (
        "Chat model name or config string to use for model responses. Example: "
        "'gpt-5.4' or 'gpt-5.4?key1=value1&key2=value2'."
    )
    openai_help: str = "Use the default OpenAI chat model."
    anthropic_help: str = "Use the default Anthropic chat model."
    google_help: str = "Use the default Google chat model."
    tool_choice_help: str = (
        "Tool choice policy for the model, such as 'auto', 'any', or a tool name."
    )
    parallel_tool_calls_help: str = (
        "Allow the model to request multiple tool calls in parallel when supported."
    )
    streaming_help: str = "Stream chat model output incrementally if supported."
    # --------------------------------------------------
    # Cost Recorder
    # --------------------------------------------------
    cost_recorder_help: str = (
        "Cost recorder name or config string to use. Example: 'null', 'local', or "
        "'local?key1=value1&key2=value2'."
    )
    # --------------------------------------------------
    # Observability
    # --------------------------------------------------
    request_logger_help: str = "Request logger name to use."
    cost_logger_help: str = "Cost logger name to use."
    chat_logger_help: str = "Chat logger name to use."
    tool_logger_help: str = "Tool logger name to use."
    finalizers_help: str = (
        "Finalizer to run after CLI execution. Repeatable and executed in the "
        "specified order. Example: 'null', 'subprocess', or a custom finalizer."
    )
    # --------------------------------------------------
    # Run Context
    # --------------------------------------------------
    organization_id_help: str = "Organization ID to use as the default run context."
    user_id_help: str = "User ID to use as the default run context."
    agent_id_help: str = "Agent ID to use as the default run context."
    node_id_help: str = "Node ID to use as the default run context."
    language_help: str = "Language code ISO 639-1 format (e.g., 'en', 'fr')."
    time_zone_help: str = "Time zone in IANA format (e.g., 'America/New_York')."
    currency_help: str = "Currency code in ISO 4217 format (e.g., 'USD', 'EUR')."
    # --------------------------------------------------
    # Config
    # --------------------------------------------------
    i18n_catalog_help: str = (
        "Additional i18n catalog file path or pattern to load. Repeatable. "
        "Matching YAML files (.yml, .yaml) are loaded before the run starts."
    )
    config_file_help: str = (
        "Additional config file path to load. Repeatable. Later files can override earlier values."
    )
    config_var_help: str = (
        "Inline user config to load after config files. Repeatable. Format: "
        "'module.path?key1=value1&nested.key2=value2'."
    )
    plugin_help: str = (
        "Additional plugin file path or pattern to load. Repeatable. Matching "
        "Python files (.py) are loaded before the run starts."
    )
    # --------------------------------------------------
    # Profile
    # --------------------------------------------------
    profile_help: str = (
        "Profile name to use for loading and saving run settings. If omitted, the "
        "current profile is used."
    )
    set_profile_help: str = (
        "Save the current run settings to the selected profile after applying CLI overrides."
    )
    reset_profile_help: str = (
        "Replace the selected profile's saved run settings with the current CLI settings."
    )
    # --------------------------------------------------
    # GitHub
    # --------------------------------------------------
    github_ignore_cache_help: str = (
        "Ignore cached GitHub files and directories and fetch them again."
    )
    github_trusted_username_help: str = (
        "GitHub username to trust without prompting during trust verification. Repeatable."
    )
    github_skip_trust_verification_help: str = "Skip GitHub trust verification for all sources."
    # --------------------------------------------------
    # Logging
    # --------------------------------------------------
    logger_name_help: str = (
        "Logger name to configure. Repeatable. If omitted, the root logger settings are used."
    )
    log_level_help: str = "Logging level to apply, such as 'DEBUG', 'INFO', or 'WARNING'."
    verbose_help: str = "Shortcut for '--log-level DEBUG'."
    quiet_help: str = "Shortcut for '--log-level WARNING'."
    # --------------------------------------------------
    # CLI
    # --------------------------------------------------
    exec_file_help: str = (
        "Load CLI arguments from a JSON, YAML, or Markdown file. Markdown front "
        "matter is used as options, and Markdown body text can be used by commands "
        "that accept content."
    )
