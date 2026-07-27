from kiari.impl.watch_handler_impl.vanilla import VanillaWatchHandler


def test_vanilla_watch_handler() -> None:
    assert issubclass(VanillaWatchHandler, object)
