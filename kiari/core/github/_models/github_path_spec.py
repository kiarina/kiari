from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

from kiarina.agi.local_scanner import LocalPathSpec

from .._types.github_path_pattern import GitHubPathPattern


@dataclass
class GitHubPathSpec:
    username: str
    repo: str
    file_path: str
    commit_hash: str | None = None
    include_patterns: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        return self.to_string()

    @property
    def is_dir(self) -> bool:
        return self.file_path.endswith("/")

    @property
    def dir_path(self) -> str:
        return self.file_path.rstrip("/")

    @property
    def blob_view_url(self) -> str:
        return (
            "https://github.com/"
            f"{self.username}/{self.repo}/blob/{self.get_commit_hash()}/{self.file_path}"
        )

    @property
    def raw_content_url(self) -> str:
        return (
            "https://raw.githubusercontent.com/"
            f"{self.username}/{self.repo}/{self.get_commit_hash()}/{self.file_path}"
        )

    @property
    def trees_api_url(self) -> str:
        return (
            "https://api.github.com/repos/"
            f"{self.username}/{self.repo}/git/trees/{self.get_commit_hash()}?recursive=1"
        )

    def get_commit_hash(self) -> str:
        return self.commit_hash or "main"

    def get_cache_path(self, cache_dir: Path | str) -> Path:
        return Path(cache_dir) / self.username / self.repo / self.file_path

    def to_string(self) -> str:
        parts: list[str] = ["@", self.username, "/", self.repo]

        if self.file_path:
            parts.extend(["/", self.file_path])

        if self.commit_hash:
            parts.extend(["@", self.commit_hash])

        if self.include_patterns or self.exclude_patterns:
            parts.append("?")

        if self.include_patterns:
            parts.append("include=" + ",".join(self.include_patterns))

        if self.include_patterns and self.exclude_patterns:
            parts.append("&")

        if self.exclude_patterns:
            parts.append("exclude=" + ",".join(self.exclude_patterns))

        return "".join(parts)

    @classmethod
    def from_string(cls, github_path_pattern: GitHubPathPattern) -> Self:
        local_path_spec = LocalPathSpec.from_string(github_path_pattern)
        path_pattern = local_path_spec.path_pattern

        if path_pattern.startswith("@"):
            path_pattern = path_pattern[1:]

        parts = path_pattern.split("@")
        path_part = parts[0]
        path_segments = path_part.split("/")

        return cls(
            username=path_segments[0],
            repo=path_segments[1],
            file_path="/".join(path_segments[2:]),
            commit_hash=parts[1] if len(parts) > 1 else None,
            include_patterns=local_path_spec.include_patterns,
            exclude_patterns=local_path_spec.exclude_patterns,
        )
