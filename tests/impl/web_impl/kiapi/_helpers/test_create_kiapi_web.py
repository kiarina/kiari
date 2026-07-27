from kiari.impl.web_impl.kiapi import KiapiWeb, create_kiapi_web


def test_create_kiapi_web() -> None:
    web = create_kiapi_web(
        kiapi_base_url="https://kiapi.example",
        timeout=30.0,
    )

    assert isinstance(web, KiapiWeb)
    assert web.settings.kiapi_base_url == "https://kiapi.example"
    assert web.settings.timeout == 30.0


def test_create_kiapi_web_defaults() -> None:
    web = create_kiapi_web()

    assert web.settings.kiapi_base_url == "http://192.168.1.37:8500"
    assert web.settings.timeout == 120.0
