from rich_click.utils import OptionGroupDict

COMMON_OPTION_GROUPS: list[OptionGroupDict] = [
    {
        "name": "History Repository",
        "options": [
            "--history-repository",
            "--stateless",
            "--no-load",
            "--no-save",
            "--allow-active-missing-tools",
        ],
    },
    {
        "name": "History",
        "options": [
            "--event",
            "--file-info",
            "--tool-info",
            "--default-tool-state",
        ],
    },
    {
        "name": "Agent",
        "options": [
            "--agent",
            "--file-limits",
            "--max-iterations",
            "--until-end",
            "--until-tool-call",
            "--until-tool-run",
        ],
    },
    {
        "name": "Tool",
        "options": [
            "--tool",
            "--pre-hook",
            "--post-hook",
        ],
    },
    {
        "name": "Workflow",
        "options": [
            "--workflow",
        ],
    },
    {
        "name": "Prompt",
        "options": [
            "--prompt",
            "--prompt-limits",
            "--system-message",
        ],
    },
    {
        "name": "Chat",
        "options": [
            "--chat-model",
            "--openai",
            "--anthropic",
            "--google",
            "--tool-choice",
            "--parallel-tool-calls",
            "--streaming",
        ],
    },
    {
        "name": "Cost Recorder",
        "options": [
            "--cost-recorder",
        ],
    },
    {
        "name": "Observability",
        "options": [
            "--request-logger",
            "--cost-logger",
            "--chat-logger",
            "--tool-logger",
        ],
    },
    {
        "name": "Run Context",
        "options": [
            "--organization-id",
            "--user-id",
            "--agent-id",
            "--runner-id",
            "--language",
            "--time-zone",
            "--currency",
        ],
    },
    {
        "name": "GitHub",
        "options": [
            "--github-ignore-cache",
            "--github-trusted-username",
            "--github-skip-trust-verification",
        ],
    },
    {
        "name": "Config",
        "options": [
            "--i18n-catalog",
            "--config",
            "--config-var",
            "--plugin",
        ],
    },
    {
        "name": "Profile",
        "options": [
            "--profile",
            "--set-profile",
            "--reset-profile",
        ],
    },
    {
        "name": "Logging",
        "options": [
            "--logger-name",
            "--log-level",
            "--verbose",
            "--quiet",
        ],
    },
]
