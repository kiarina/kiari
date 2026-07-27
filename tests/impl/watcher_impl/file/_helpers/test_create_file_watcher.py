from kiari.impl.watcher_impl.file import FileWatcher, create_file_watcher


def test_create_file_watcher() -> None:
    watcher = create_file_watcher(paths=["src"], debounce=0.5)

    assert isinstance(watcher, FileWatcher)
    assert watcher.settings.paths == ["src"]
    assert watcher.settings.debounce == 0.5


def test_from_string_list() -> None:
    watcher = create_file_watcher(
        paths="src,tests",
        include_patterns="*.py",
        change_types="modified",
    )

    assert watcher.settings.paths == ["src", "tests"]
    assert watcher.settings.include_patterns == ["*.py"]
    assert watcher.settings.change_types == ["modified"]
