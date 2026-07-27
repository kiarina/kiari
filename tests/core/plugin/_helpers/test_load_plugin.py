import pytest

from kiari.core.plugin import load_plugin


async def test_setup_plugin(tmp_path, capsys) -> None:
    (tmp_path / "test_plugin.py").write_text('print("Hello from plugin.")')
    await load_plugin(str(tmp_path / "test_plugin.py"))
    assert "Hello from plugin." in capsys.readouterr().out

    await load_plugin(str(tmp_path / "test_plugin.py"))  # cached


async def test_import_error(tmp_path) -> None:
    (tmp_path / "bad_plugin.py").write_text("import non_existent_module")

    with pytest.raises(ImportError):
        await load_plugin(str(tmp_path / "bad_plugin.py"))
