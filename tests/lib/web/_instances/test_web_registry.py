import pytest

from kiari.impl.web_impl.kiapi import KiapiWeb
from kiari.lib.web import BaseWeb, web_registry


@pytest.fixture(autouse=True)
def cleanup():
    yield
    web_registry.clear()


def test_web_registry() -> None:
    class ExampleWeb(BaseWeb):
        pass

    web_registry.register("test", ExampleWeb)

    web = web_registry.create("test", value="example")

    assert isinstance(web, ExampleWeb)
    assert web.name == "test"
    assert web.init_kwargs == {"value": "example"}


def test_web_registry_resolves_default() -> None:
    web = web_registry.resolve()

    assert isinstance(web, KiapiWeb)
    assert web.name == "kiapi"
