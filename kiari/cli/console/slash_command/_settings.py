from kiarina.utils.common import ImportPath
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from ._types.slash_command_name import SlashCommandName


class SlashCommandSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI_SLASH_COMMAND_",
        extra="ignore",
    )

    aliases: dict[SlashCommandName, SlashCommandName] = Field(
        default_factory=lambda: {
            "a": "attach",
            "b": "back",
            "cm": "chat_model",
            "c": "clear",
            "cp": "copy",
            "e": "event",
            "fi": "file_info",
            "file": "file_info",
            "h": "help",
            "m": "metadata",
            "r": "run",
            "s": "show",
            "t": "tool",
            "tc": "tool_choice",
            "ti": "tool_info",
        }
    )

    presets: dict[SlashCommandName, ImportPath] = Field(
        default_factory=lambda: {
            "attach": "kiari.cli.console.slash_command_impl.attach:AttachSlashCommand",
            "back": "kiari.cli.console.slash_command_impl.back:BackSlashCommand",
            "chat_model": "kiari.cli.console.slash_command_impl.chat_model:ChatModelSlashCommand",
            "clear": "kiari.cli.console.slash_command_impl.clear:ClearSlashCommand",
            "copy": "kiari.cli.console.slash_command_impl.copy:CopySlashCommand",
            "event": "kiari.cli.console.slash_command_impl.event:EventSlashCommand",
            "file_info": "kiari.cli.console.slash_command_impl.file_info:FileInfoSlashCommand",
            "help": "kiari.cli.console.slash_command_impl.help:HelpSlashCommand",
            "metadata": "kiari.cli.console.slash_command_impl.metadata:MetadataSlashCommand",
            "run": "kiari.cli.console.slash_command_impl.run:RunSlashCommand",
            "show": "kiari.cli.console.slash_command_impl.show:ShowSlashCommand",
            "stt": "kiari.cli.console.slash_command_impl.stt:STTSlashCommand",
            "tool": "kiari.cli.console.slash_command_impl.tool:ToolSlashCommand",
            "tool_choice": "kiari.cli.console.slash_command_impl.tool_choice:ToolChoiceSlashCommand",
            "tool_info": "kiari.cli.console.slash_command_impl.tool_info:ToolInfoSlashCommand",
            "tts": "kiari.cli.console.slash_command_impl.tts:TTSSlashCommand",
        }
    )
    customs: dict[SlashCommandName, ImportPath] = Field(default_factory=dict)


settings_manager = SettingsManager(SlashCommandSettings)
