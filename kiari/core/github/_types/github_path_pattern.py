type GitHubPathPattern = str
"""
A string in one of the following formats:

- {GitHubPath}
- {GitHubPath}?{ConfigString}

Formats:

- GitHubPath: A string in the format ``@owner/repo/path/to/file_or_dir``, where:
    - owner: GitHub username or organization name
    - repo: GitHub repository name
    - path/to/file_or_dir: Path to a file or directory in the repository. If it ends with a slash, it is treated as a directory.
- ConfigString: A query string with the following optional parameters:
    - include: file patterns to include when scanning a directory (comma-separated)
    - exclude: file patterns to exclude when scanning a directory (comma-separated)

Examples:
- "@kiarina/pydantic-settings-manager/README.md"
- "@kiarina/pydantic-settings-manager/tests/?include=*.py&exclude=__init__.py"
"""
