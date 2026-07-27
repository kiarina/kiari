from kiari.lib.gui import gui


def test_gui() -> None:
    print(f"monitor: {gui.monitor}")
    print(f"mouse: {gui.mouse}")
    print(f"keyboard: {gui.keyboard}")

    assert True
