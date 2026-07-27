from kiarina.utils.common import ImportPath
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._types.streamlit_handler_name import StreamlitHandlerName
from ._types.streamlit_handler_specifier import StreamlitHandlerSpecifier


class StreamlitHandlerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KIARI_STREAMLIT_HANDLER_", extra="ignore")

    default: StreamlitHandlerSpecifier = "vanilla"
    presets: dict[StreamlitHandlerName, ImportPath] = Field(
        default_factory=lambda: {
            "vanilla": "kiari.impl.streamlit_handler_impl.vanilla:VanillaStreamlitHandler"
        }
    )
    customs: dict[StreamlitHandlerName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(StreamlitHandlerSettings)
