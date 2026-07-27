from pathlib import Path

from kiarina.utils.file.asyncio import read_yaml_dict, write_yaml_dict

from kiari.core.paths import get_github_trusted_sources_file_path


class GitHubTrustedSourceStore:
    @property
    def file_path(self) -> Path:
        return get_github_trusted_sources_file_path()

    async def load(self) -> list[str]:
        data = await read_yaml_dict(str(self.file_path), default={})
        trusted_sources = data.get("trusted", [])
        if not isinstance(trusted_sources, list) or not all(
            isinstance(source, str) for source in trusted_sources
        ):
            raise TypeError("GitHub trusted sources must be a list of strings")
        return trusted_sources

    async def save(self, trusted_sources: list[str]) -> None:
        await write_yaml_dict(str(self.file_path), {"trusted": trusted_sources})

    async def delete(self) -> None:
        if self.file_path.exists():
            self.file_path.unlink()


github_trusted_source_store = GitHubTrustedSourceStore()
