from kiarina.agi.file_info_builder import FileInfoSpecifier
from kiarina.agi.file_utils import is_uri
from kiarina.utils.common import parse_config_string

from kiari.core.file_resolver import resolve_file_paths

from .._types.file_info_source import FileInfoSource


async def resolve_file_info_specifiers(
    source: FileInfoSource | list[FileInfoSource],
) -> list[FileInfoSpecifier]:
    if not isinstance(source, list):
        source = [source]

    return [
        file_info_specifier
        for file_info_source in source
        for file_info_specifier in await _resolve(file_info_source)
    ]


async def _resolve(source: FileInfoSource) -> list[FileInfoSpecifier]:
    if not _should_resolve_file_pattern(source):
        return [source]

    if "?" in source:
        path_part, config_string = source.split("?", 1)
    else:
        path_part, config_string = source, ""

    config = parse_config_string(config_string, separator="&", key_value_separator="=")

    include = config.pop("include", "")
    exclude = config.pop("exclude", "")

    file_pattern = f"{path_part}?include={include}&exclude={exclude}"
    config_string = _build_config_string(config)

    return [f"{file_path}{config_string}" for file_path in await resolve_file_paths(file_pattern)]


def _should_resolve_file_pattern(source: FileInfoSource) -> bool:
    if source.startswith("{"):
        return False

    if is_uri(source):
        return False

    return True


def _build_config_string(config: dict[str, str]) -> str:
    if not config:
        return ""

    return "?" + "&".join(f"{key}={value}" for key, value in config.items())
