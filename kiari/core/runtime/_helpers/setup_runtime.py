import logging
from typing import Any

from kiarina.i18n import catalog
from kiarina.utils.common import parse_config_string
from kiarina.utils.file import read_yaml_dict
from pydantic_settings_manager import load_user_configs, update_dict

from kiari.core import file_resolver, paths, plugin
from kiari.core.logging import setup_logger
from kiari.core.profile import ProfileName, RunOptions

logger = logging.getLogger(__name__)


async def setup_runtime(profile_name: ProfileName, run_options: RunOptions) -> None:
    _setup_logger(run_options)

    _register_cost_logger()
    _register_chat_logger()
    _register_tool_logger()
    _register_tools()

    _load_global_config()
    _load_profile_config(profile_name)
    _load_config_vars(run_options)

    _setup_github(run_options)

    await _load_extra_configs(run_options)
    await _load_i18n_catalogs(run_options)
    await _load_plugins(run_options)

    _setup_run_context(run_options)

    await _load_exchange_rate(run_options)

    _setup_cost_recorder(run_options)
    _setup_cost_logger(run_options)
    _setup_request_logger(run_options)
    _setup_chat_logger(run_options)
    _setup_tool_logger(run_options)


def _setup_logger(run_options: RunOptions) -> None:
    setup_logger(
        logger_names=run_options.logger_names,
        log_level=run_options.log_level,
    )


def _register_cost_logger() -> None:
    from kiarina.agi.cost_logger import settings_manager

    settings_manager.set_cli_args(
        "presets",
        {
            **settings_manager.settings.presets,
            "default": "kiari.impl.cost_logger_impl.default:DefaultCostLogger",
        },
    )


def _register_chat_logger() -> None:
    from kiarina.agi.chat_logger import settings_manager

    settings_manager.set_cli_args(
        "presets",
        {
            **settings_manager.settings.presets,
            "default": "kiari.impl.chat_logger_impl.default:DefaultChatLogger",
        },
    )


def _register_tool_logger() -> None:
    from kiarina.agi.tool_logger import settings_manager

    settings_manager.set_cli_args(
        "presets",
        {
            **settings_manager.settings.presets,
            "default": "kiari.impl.tool_logger_impl.default:DefaultToolLogger",
        },
    )


def _register_tools() -> None:
    from kiarina.agi.tool import settings_manager

    settings_manager.set_cli_args(
        "presets",
        {
            **settings_manager.settings.presets,
            "subprocess": "kiari.impl.tool_impl.subprocess:Subprocess",
            "change_directory": "kiari.impl.tool_impl.change_directory:ChangeDirectory",
            "chrome": "kiari.impl.tool_impl.chrome:Chrome",
            "gui": "kiari.impl.tool_impl.gui:Gui",
            "audio_file_view": "kiari.impl.tool_impl.audio_file_view:AudioFileView",
            "image_generate": "kiari.impl.tool_impl.image_generate:ImageGenerate",
            "image_file_view": "kiari.impl.tool_impl.image_file_view:ImageFileView",
            "pdf_file_view": "kiari.impl.tool_impl.pdf_file_view:PdfFileView",
            "text_file_view": "kiari.impl.tool_impl.text_file_view:TextFileView",
            "text_file_edit": "kiari.impl.tool_impl.text_file_edit:TextFileEdit",
            "video_predict": "kiari.impl.tool_impl.video_predict:VideoPredict",
            "video_file_view": "kiari.impl.tool_impl.video_file_view:VideoFileView",
            "web": "kiari.impl.tool_impl.web:Web",
        },
    )


def _load_global_config() -> None:
    file_path = paths.get_config_file_path()

    if user_configs := read_yaml_dict(file_path):
        load_user_configs(user_configs)
        logger.info(f"Loaded global config from {file_path}")


def _load_profile_config(profile_name: ProfileName) -> None:
    file_path = paths.get_profile_config_file_path(profile_name)

    if user_configs := read_yaml_dict(file_path):
        load_user_configs(user_configs, update_policy="merge")
        logger.info(f"Loaded profile config from {file_path}")


def _load_config_vars(run_options: RunOptions) -> None:
    user_configs: dict[str, Any] = {}

    for config_var in run_options.config_vars:
        module_name, config_str = _parse_config_var(config_var)
        config = parse_config_string(
            config_str,
            separator="&",
            key_value_separator="=",
        )
        user_configs = update_dict(user_configs, {module_name: config})

    if user_configs:
        load_user_configs(user_configs, update_policy="merge")
        logger.info("Loaded config vars")


def _parse_config_var(config_var: str) -> tuple[str, str]:
    if "?" not in config_var:  # pragma: no cover
        raise ValueError(
            "Invalid config var. Expected format: 'module.path?key1=value1&key2=value2'."
        )

    module_name, config_str = config_var.split("?", 1)

    if not module_name or not config_str:  # pragma: no cover
        raise ValueError(
            "Invalid config var. Expected format: 'module.path?key1=value1&key2=value2'."
        )

    return module_name, config_str


async def _load_extra_configs(run_options: RunOptions) -> None:
    file_paths = await file_resolver.resolve_file_paths(run_options.configs)
    yaml_file_paths = [
        file_path for file_path in file_paths if file_path.endswith((".yml", ".yaml"))
    ]

    for file_path in yaml_file_paths:
        if user_configs := read_yaml_dict(file_path):
            load_user_configs(user_configs, update_policy="merge")
            logger.info(f"Loaded extra config from {file_path}")


def _setup_github(run_options: RunOptions) -> None:
    from kiari.core.github import settings_manager

    if run_options.github_ignore_cache is not None:
        settings_manager.set_cli_args("ignore_cache", run_options.github_ignore_cache)

    if run_options.github_trusted_usernames:
        settings_manager.set_cli_args("trusted_usernames", run_options.github_trusted_usernames)

    if run_options.github_skip_trust_verification is not None:
        settings_manager.set_cli_args(
            "skip_trust_verification", run_options.github_skip_trust_verification
        )


async def _load_i18n_catalogs(run_options: RunOptions) -> None:
    file_paths = await file_resolver.resolve_file_paths(run_options.i18n_catalogs)

    yaml_file_paths = [
        file_path for file_path in file_paths if file_path.endswith((".yml", ".yaml"))
    ]

    for file_path in yaml_file_paths:
        catalog.add_from_file(file_path)
        logger.debug(f"Loaded i18n catalog from {file_path}")


async def _load_plugins(run_options: RunOptions) -> None:
    file_paths = await file_resolver.resolve_file_paths(run_options.plugins)

    python_file_paths = [file_path for file_path in file_paths if file_path.endswith(".py")]

    for file_path in python_file_paths:
        await plugin.load_plugin(file_path)


async def _load_exchange_rate(run_options: RunOptions) -> None:
    from kiarina.agi.run_context import RunContext

    from kiari.core.exchange_rate import exchange_rate_store

    await exchange_rate_store.load(run_options.currency or RunContext().currency)


def _setup_run_context(run_options: RunOptions) -> None:
    import secrets
    import string

    from kiarina.agi.run_context import settings_manager
    from kiarina.currency import get_system_currency
    from kiarina.i18n import get_system_language
    from kiarina.utils.app import user_directory
    from tzlocal import get_localzone

    settings_manager.set_cli_args("organization_id", run_options.organization_id)
    settings_manager.set_cli_args("user_id", run_options.user_id)
    settings_manager.set_cli_args("agent_id", run_options.agent_id)

    if run_options.node_id is not None:
        settings_manager.set_cli_args("node_id", run_options.node_id)
    else:
        path = user_directory.get_user_data_dir() / "node_id.txt"

        if path.exists():
            node_id = path.read_text().strip()
        else:
            node_id = secrets.choice(string.ascii_lowercase) + "".join(
                secrets.choice(string.ascii_lowercase + string.digits) for _ in range(5)
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(node_id)

        settings_manager.set_cli_args("node_id", node_id)

    settings_manager.set_cli_args("time_zone", run_options.time_zone or str(get_localzone()))

    settings_manager.set_cli_args(
        "language",
        run_options.language or get_system_language(),
    )

    settings_manager.set_cli_args(
        "currency",
        run_options.currency or get_system_currency(),
    )


def _setup_cost_recorder(run_options: RunOptions) -> None:
    from kiarina.agi.cost_recorder import settings_manager

    settings_manager.set_cli_args("default", run_options.cost_recorder)


def _setup_cost_logger(run_options: RunOptions) -> None:
    from kiarina.agi.cost_logger import settings_manager
    from kiarina.agi.run_context import RunContext
    from kiarina.currency import CurrencyCode

    from kiari.core.exchange_rate import (
        ExchangeRateNotLoadedError,
        exchange_rate_store,
    )

    currency: CurrencyCode | None = None
    exchange_rate: float | None = None

    try:
        currency = run_options.currency or RunContext().currency
        exchange_rate = exchange_rate_store.get(currency)
    except ExchangeRateNotLoadedError:
        currency = None
        exchange_rate = None

    settings_manager.set_cli_args("default", run_options.cost_logger)
    settings_manager.set_cli_args("currency", currency)
    settings_manager.set_cli_args("exchange_rate", exchange_rate)


def _setup_request_logger(run_options: RunOptions) -> None:
    from kiarina.agi.request_logger import settings_manager

    settings_manager.set_cli_args("default", run_options.request_logger)


def _setup_chat_logger(run_options: RunOptions) -> None:
    from kiarina.agi.chat_logger import settings_manager

    settings_manager.set_cli_args("default", run_options.chat_logger)


def _setup_tool_logger(run_options: RunOptions) -> None:
    from kiarina.agi.tool_logger import settings_manager

    settings_manager.set_cli_args("default", run_options.tool_logger)
