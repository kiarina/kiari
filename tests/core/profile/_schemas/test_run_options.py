import pytest
from pydantic import ValidationError

from kiari.core.finalizer import settings_manager as finalizer_settings_manager
from kiari.core.profile import RunOptions


def test_default_finalizers_do_not_own_chrome() -> None:
    assert RunOptions().finalizers == ["subprocess"]
    assert "chrome" not in finalizer_settings_manager.settings.presets


def test_timezone() -> None:
    assert RunOptions(timezone="Asia/Tokyo").timezone == "Asia/Tokyo"


def test_rejects_old_time_zone_field() -> None:
    with pytest.raises(ValidationError, match="time_zone was renamed to timezone"):
        RunOptions.model_validate({"time_zone": "Asia/Tokyo"})
