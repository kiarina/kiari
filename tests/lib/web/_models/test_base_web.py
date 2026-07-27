import pytest

from kiari.lib.web import BaseWeb


async def test_base_web() -> None:
    web = BaseWeb(example="value")
    web.name = "example"

    assert web.name == "example"
    assert web.init_kwargs == {"example": "value"}
    assert str(web) == "BaseWeb"

    with pytest.raises(NotImplementedError):
        await web.search("query")

    with pytest.raises(NotImplementedError):
        await web.fetch("https://example.com")
