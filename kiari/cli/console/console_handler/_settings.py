from kiarina.utils.common import ImportPath
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._types.console_handler_name import ConsoleHandlerName
from ._types.console_handler_specifier import ConsoleHandlerSpecifier


class ConsoleHandlerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI_CONSOLE_HANDLER_",
        extra="ignore",
    )

    default: ConsoleHandlerSpecifier = "vanilla"

    presets: dict[ConsoleHandlerName, ImportPath] = Field(
        default_factory=lambda: {
            "vanilla": "kiari.impl.console_handler_impl.vanilla:VanillaConsoleHandler",
        }
    )

    customs: dict[ConsoleHandlerName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(ConsoleHandlerSettings)
