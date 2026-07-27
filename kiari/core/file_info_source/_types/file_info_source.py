from kiarina.agi.file_info_builder import FileInfoSpecifier
from kiarina.agi.local_scanner import LocalPathPattern

from kiari.core.github import GitHubPathPattern

type FileInfoSource = LocalPathPattern | GitHubPathPattern | FileInfoSpecifier
"""
A string in one of the following formats:

- {LocalPathPattern}
- {GitHubPathPattern}
- {FileInfoSpecifier}

Additionally, parameters equivalent to FileInfoSpecifier can be specified as query parameters in LocalPathPattern and GitHubPathPattern.

Examples:
- "README.md"
- "src/?include=*.py&exclude=test_*.py&group=hello"
- "@kiarina/pydantic-settings-manager/README.md"
- "@kiarina/pydantic-settings-manager/tests/?include=*.py&exclude=__init__.py&group=hello"
- '{"uri_or_file_path": "/path/to/file.txt", "start_line": 10, "end_line": 20}'
"""
