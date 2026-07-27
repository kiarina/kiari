from .history_repository_name import HistoryRepositoryName

type HistoryRepositorySpecifier = HistoryRepositoryName | str
"""
A string in the form of "{HistoryRepositoryName}?{ConfigString}"

Examples:
- "my_history_repository"
- "my_preset_repository?key1=value1&key2=value2"
"""
