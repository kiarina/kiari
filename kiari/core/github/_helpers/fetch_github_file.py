import logging
import os
from pathlib import Path
from typing import Any

import httpx
from kiarina.agi.file import FilePath
from kiarina.utils import mime
from kiarina.utils.file.asyncio import FileBlob, read_file, write_file

from .._models.github_path_spec import GitHubPathSpec
from .._settings import settings_manager
from .._types.github_path_pattern import GitHubPathPattern

type RawContent = bytes

logger = logging.getLogger(__name__)


async def fetch_github_file(
    github_path: GitHubPathPattern | GitHubPathSpec,
    *,
    cache_dir: Path | str,
    ignore_cache: bool | None = None,
) -> FilePath:
    settings = settings_manager.get_settings()

    if ignore_cache is None:
        ignore_cache = settings.ignore_cache

    if isinstance(github_path, str):
        spec = GitHubPathSpec.from_string(github_path)
    else:
        spec = github_path

    cache_path = spec.get_cache_path(cache_dir)

    if cache_path.is_dir():
        raise IsADirectoryError(str(cache_path))

    if cache_path.exists() and not ignore_cache:
        if file_blob := await read_file(str(cache_path)):
            return file_blob.file_path

    raw_content = await _fetch_github_file_content(spec)

    mime_blob = mime.create_mime_blob(raw_content)
    file_blob = FileBlob(str(cache_path), mime_blob)
    await write_file(file_blob)

    return file_blob.file_path


async def _fetch_github_file_content(spec: GitHubPathSpec) -> RawContent:
    settings = settings_manager.get_settings()

    headers: dict[str, Any] = {}

    if settings.access_token:
        headers["Authorization"] = f"token {settings.access_token.get_secret_value()}"
    elif github_token := os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"token {github_token}"

    logger.info(f"Fetching from GitHub: {spec.blob_view_url}")

    async with httpx.AsyncClient() as client:
        response = await client.get(spec.raw_content_url, headers=headers)
        response.raise_for_status()
        return response.content
