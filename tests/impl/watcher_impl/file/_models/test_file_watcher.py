import json
from pathlib import Path

from watchfiles import Change

from kiari.impl.watcher_impl.file import (
    FileChange,
    FileWatcher,
    FileWatcherSettings,
    FileWatchEvent,
    FileWatchPayload,
)


def test_filter_changes() -> None:
    watcher = FileWatcher(
        FileWatcherSettings(
            include_patterns=["*.py"],
            exclude_patterns=["*_test.py"],
            change_types=["modified"],
        )
    )

    changes = {
        (Change.modified, "src/app.py"),
        (Change.added, "src/new.py"),
        (Change.modified, "src/app_test.py"),
        (Change.modified, "README.md"),
    }

    filtered = watcher._filter_changes(changes)

    assert [(change.name.lower(), str(path)) for change, path in filtered] == [
        ("modified", "src/app.py")
    ]


def test_build_file_changes_text() -> None:
    watcher = FileWatcher(FileWatcherSettings())
    watcher.name = "file"

    text = watcher._build_file_changes_text(
        [
            (Change.modified, Path("b.txt")),
            (Change.added, Path("a.txt")),
        ]
    )

    assert json.loads(text) == {
        "type": "file_changes",
        "changes": [
            {
                "change_type": "added",
                "file_path": "a.txt",
            },
            {
                "change_type": "modified",
                "file_path": "b.txt",
            },
        ],
    }


def test_file_watch_event_changes() -> None:
    event = FileWatchEvent.create(
        watcher_name="file",
        changes=[
            FileChange(change_type="modified", file_path="src/app.py"),
        ],
    )

    assert event.changes == [FileChange(change_type="modified", file_path="src/app.py")]
    assert event.payload == FileWatchPayload(changes=event.changes)
