from kiarina.utils.common import ImportPath
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._types.schedule_handler_name import ScheduleHandlerName
from ._types.schedule_handler_specifier import ScheduleHandlerSpecifier


class ScheduleHandlerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI2_SCHEDULE_HANDLER_",
        extra="ignore",
    )

    default: ScheduleHandlerSpecifier = "vanilla"

    presets: dict[ScheduleHandlerName, ImportPath] = Field(
        default_factory=lambda: {
            "vanilla": "kiari.impl.schedule_handler_impl.vanilla:VanillaScheduleHandler",
        }
    )

    customs: dict[ScheduleHandlerName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(ScheduleHandlerSettings)
