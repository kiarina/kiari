from kiarina.agi.local_scanner import LocalPathPattern

from kiari.core.github import GitHubPathPattern

type FilePathPattern = LocalPathPattern | GitHubPathPattern
