from kiari.core.profile import RunOptions
from kiari.fastapi.fastapi_handler import BaseFastAPIHandler, fastapi_handler_registry


def test_fastapi_handler_registry() -> None:
    handler = fastapi_handler_registry.resolve(
        "vanilla?example=value",
        profile_name="test",
        run_options=RunOptions(),
    )

    assert isinstance(handler, BaseFastAPIHandler)
    assert handler.name == "vanilla"
    assert handler.init_kwargs == {"example": "value"}
