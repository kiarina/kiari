from kiari.impl.watcher_impl.pubsub import PubsubWatcher, create_pubsub_watcher


def test_create_pubsub_watcher() -> None:
    watcher = create_pubsub_watcher(project_id="project", subscription_id="sub")

    assert isinstance(watcher, PubsubWatcher)
    assert watcher.settings.project_id == "project"
    assert watcher.settings.subscription_id == "sub"
