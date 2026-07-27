from .watcher_name import WatcherName

type WatcherSpecifier = WatcherName | str
"""
A string in the form of "{WatcherName}?{ConfigString}"

Examples:
- "file"
- "file?paths=src&debounce=0.5"
"""
