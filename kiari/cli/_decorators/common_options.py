import functools
from collections.abc import Callable
from typing import Any

import rich_click as click
from kiarina.i18n import get_i18n, get_system_language

from .._i18n import CLII18n

t = get_i18n(CLII18n, get_system_language())


def common_options[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    # fmt: off
    # --------------------------------------------------
    # History Repository
    # --------------------------------------------------
    @click.option("--history-repository", type=str, help=t.history_repository_help)
    @click.option("--stateless", is_flag=True, is_eager=True, expose_value=False, callback=_set_stateless, help=t.stateless_help)
    @click.option("--no-load", is_flag=True, default=None, help=t.no_load_help)
    @click.option("--no-save", is_flag=True, default=None, help=t.no_save_help)
    @click.option("--allow-active-missing-tools", is_flag=True, default=None, help=t.allow_active_missing_tools_help)
    # --------------------------------------------------
    # History
    # --------------------------------------------------
    @click.option("--event", "events", multiple=True, type=str, help=t.events_help)
    @click.option("-f", "--file-info", "file_infos", multiple=True, type=str, help=t.file_infos_help)
    @click.option("--tool-info", "tool_infos", multiple=True, type=str, help=t.tool_infos_help)
    @click.option("--default-tool-state", type=click.Choice(["active", "inactive", "disabled"]), help=t.default_tool_state_help)
    # --------------------------------------------------
    # Agent
    # --------------------------------------------------
    @click.option("--agent", type=str, help=t.agent_help)
    @click.option("--file-limits", type=str, help=t.file_limits_help)
    @click.option("-n", "--max-iterations", type=int, help=t.max_iterations_help)
    @click.option("--until-end/--no-until-end", is_flag=True, default=None, help=t.until_end_help)
    @click.option("--until-tool-call", "until_tool_calls", multiple=True, type=str, help=t.until_tool_calls_help)
    @click.option("--until-tool-run", "until_tool_runs", multiple=True, type=str, help=t.until_tool_runs_help)
    # --------------------------------------------------
    # Tool
    # --------------------------------------------------
    @click.option("-t", "--tool", "tools", multiple=True, type=str, help=t.tools_help)
    @click.option("--pre-hook", "pre_hooks", multiple=True, type=str, help=t.pre_hooks_help)
    @click.option("--post-hook", "post_hooks", multiple=True, type=str, help=t.post_hooks_help)
    # --------------------------------------------------
    # Workflow
    # --------------------------------------------------
    @click.option("--workflow", type=str, help=t.workflow_help)
    # --------------------------------------------------
    # Prompt
    # --------------------------------------------------
    @click.option("--prompt", type=str, help=t.prompt_help)
    @click.option("--prompt-limits", type=str, help=t.prompt_limits_help)
    @click.option("--system-message", "system_messages", multiple=True, type=str, help=t.system_messages_help)
    # --------------------------------------------------
    # Chat
    # --------------------------------------------------
    @click.option("--chat-model", type=str, help=t.chat_model_help)
    @click.option("--openai", is_flag=True, default=None, is_eager=True, expose_value=False, callback=_set_openai, help=t.openai_help)
    @click.option("--anthropic", is_flag=True, default=None, is_eager=True, expose_value=False, callback=_set_anthropic, help=t.anthropic_help)
    @click.option("--google", is_flag=True, default=None, is_eager=True, expose_value=False, callback=_set_google, help=t.google_help)
    @click.option("--tool-choice", type=str, help=t.tool_choice_help)
    @click.option("--parallel-tool-calls/--no-parallel-tool-calls", default=None, help=t.parallel_tool_calls_help)
    @click.option("--streaming/--no-streaming", default=None, help=t.streaming_help)
    # --------------------------------------------------
    # Cost Recorder
    # --------------------------------------------------
    @click.option("--cost-recorder", type=str, help=t.cost_recorder_help)
    # --------------------------------------------------
    # Observability
    # --------------------------------------------------
    @click.option("--request-logger", type=str, help=t.request_logger_help)
    @click.option("--cost-logger", type=str, help=t.cost_logger_help)
    @click.option("--chat-logger", type=str, help=t.chat_logger_help)
    @click.option("--tool-logger", type=str, help=t.tool_logger_help)
    # --------------------------------------------------
    # Run Context
    # --------------------------------------------------
    @click.option("--organization-id", type=str, help=t.organization_id_help)
    @click.option("--user-id", type=str, help=t.user_id_help)
    @click.option("--agent-id", type=str, help=t.agent_id_help)
    @click.option("--runner-id", type=str, help=t.node_id_help)
    @click.option("--language", type=str, help=t.language_help)
    @click.option("--time-zone", type=str, help=t.time_zone_help)
    @click.option("--currency", type=str, help=t.currency_help)
    # --------------------------------------------------
    # GitHub
    # --------------------------------------------------
    @click.option("--github-ignore-cache", is_flag=True, default=None, help=t.github_ignore_cache_help)
    @click.option("--github-trusted-username", "github_trusted_usernames", multiple=True, type=str, help=t.github_trusted_username_help)
    @click.option("--github-skip-trust-verification", is_flag=True, default=None, help=t.github_skip_trust_verification_help)
    @functools.wraps(func)
    # --------------------------------------------------
    # Config
    # --------------------------------------------------
    @click.option("--i18n-catalog", "i18n_catalogs", multiple=True, type=str, help=t.i18n_catalog_help)
    @click.option("--config", "configs", multiple=True, type=str, help=t.config_file_help)
    @click.option("-c", "--config-var", "config_vars", multiple=True, type=str, help=t.config_var_help)
    @click.option("--plugin", "plugins", multiple=True, type=str, help=t.plugin_help)
    # --------------------------------------------------
    # Logging
    # --------------------------------------------------
    @click.option("--logger-name", "logger_names", multiple=True, type=str, help=t.logger_name_help)
    @click.option("--log-level", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]), default=None, help=t.log_level_help)
    @click.option("-v", "--verbose", is_flag=True, default=None, callback=_set_verbose, help=t.verbose_help)
    @click.option("-q", "--quiet", is_flag=True, default=None, callback=_set_quiet, help=t.quiet_help)
    # --------------------------------------------------
    # Profile
    # --------------------------------------------------
    @click.option("-p", "--profile", "profile_name", type=str, default=None, help=t.profile_help)
    @click.option("--set", "--set-profile", is_flag=True, is_eager=True, expose_value=False, callback=_set_profile, help=t.set_profile_help)
    @click.option("--reset", "--reset-profile", is_flag=True, is_eager=True, expose_value=False, callback=_reset_profile, help=t.reset_profile_help)
    # --------------------------------------------------
    # CLI
    # --------------------------------------------------
    @click.option("-x", "--exec", "exec_file", type=str, help=t.exec_file_help)
    @click.option("--finalizer", "finalizers", multiple=True, type=str, help=t.finalizers_help)
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # fmt: on
        return func(*args, **kwargs)

    return wrapper


def _set_profile(ctx: click.Context, _: click.Parameter, value: Any) -> Any:
    if not value:
        return value

    ctx.params["save_mode"] = "set"
    return value


def _reset_profile(ctx: click.Context, _: click.Parameter, value: Any) -> Any:
    if not value:
        return value

    ctx.params["save_mode"] = "reset"
    return value


def _set_stateless(ctx: click.Context, _: click.Parameter, value: Any) -> Any:
    if not value:
        return value

    ctx.params["no_load"] = True
    ctx.params["no_save"] = True
    return value


def _set_openai(ctx: click.Context, _: click.Parameter, value: Any) -> Any:
    if not value:
        return value

    ctx.params["chat_model"] = "openai"
    return value


def _set_anthropic(ctx: click.Context, _: click.Parameter, value: Any) -> Any:
    if not value:
        return value

    ctx.params["chat_model"] = "anthropic"
    return value


def _set_google(ctx: click.Context, _: click.Parameter, value: Any) -> Any:
    if not value:
        return value

    ctx.params["chat_model"] = "google"
    return value


def _set_verbose(ctx: click.Context, _: click.Parameter, value: Any) -> Any:
    if not value:
        return value

    ctx.params["log_level"] = "DEBUG"
    return value


def _set_quiet(ctx: click.Context, _: click.Parameter, value: Any) -> Any:
    if not value:
        return value

    ctx.params["log_level"] = "WARNING"
    return value
