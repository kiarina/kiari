from kiari.core.finalizer import settings_manager as finalizer_settings_manager
from kiari.core.profile import RunOptions


def test_default_finalizers_do_not_own_chrome() -> None:
    assert RunOptions().finalizers == ["subprocess"]
    assert "chrome" not in finalizer_settings_manager.settings.presets
