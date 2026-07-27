from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from kiarina.utils.app import user_directory

from kiari.impl.watcher_impl.slack import SlackWatcher, SlackWatcherSettings


async def test_save_attachment(tmp_path: Path) -> None:
    watcher = SlackWatcher(SlackWatcherSettings(attachment_dir=str(tmp_path)))

    source = await watcher._save_attachment("hello world.txt", b"hello")
    split = urlsplit(source)

    assert Path(split.path).read_bytes() == b"hello"
    assert parse_qs(split.query) == {"display_name": ["hello world.txt"]}
    assert Path(split.path).name.endswith("-hello_world.txt")


def test_get_default_attachment_dir() -> None:
    watcher = SlackWatcher(SlackWatcherSettings())

    assert (
        watcher._get_attachment_dir() == user_directory.get_user_cache_dir() / "watcher" / "slack"
    )
