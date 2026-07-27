from kiari.core.profile import RunOptions
from kiari.fastapi.fastapi_handler import BaseFastAPIHandler
from kiari.impl.fastapi_handler_impl.vanilla import VanillaFastAPIHandler


def test_vanilla_fastapi_handler() -> None:
    handler = VanillaFastAPIHandler("test", RunOptions())
    assert isinstance(handler, BaseFastAPIHandler)
