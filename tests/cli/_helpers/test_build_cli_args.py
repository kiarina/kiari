import pytest

from kiari.cli import build_cli_args


def test_normalize() -> None:
    cli_args = build_cli_args(key1=None, key2=(1, 2))
    assert cli_args.run_spec == {"key2": [1, 2]}


def test_json(tmp_path) -> None:
    json_file = tmp_path / "args.json"
    json_file.write_text('{"key1": "value1", "key2": 2}')

    cli_args = build_cli_args(exec_file=str(json_file))
    assert cli_args.run_spec == {"key1": "value1", "key2": 2}


def test_yaml(tmp_path) -> None:
    yaml_file = tmp_path / "args.yaml"
    yaml_file.write_text("key1: value1\nkey2: 2")

    cli_args = build_cli_args(exec_file=str(yaml_file))
    assert cli_args.run_spec == {"key1": "value1", "key2": 2}


def test_markdown(tmp_path) -> None:
    md_file = tmp_path / "args.md"
    md_file.write_text(
        """---\n"""
        """key1: value1\n"""
        """key2: 2\n"""
        """---\n"""
        """Hello\n"""
    )

    cli_args = build_cli_args(
        exec_file=str(md_file),
        markdown_content_key="markdown_content",
    )

    assert cli_args.run_spec == {"key1": "value1", "key2": 2}
    assert cli_args.extra_args == {"markdown_content": "Hello\n"}


def test_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        build_cli_args(exec_file="non_existent_file.json")


def test_extra_args() -> None:
    cli_args = build_cli_args(key1="value1", key2="value2", extra_args_keys=["key2"])
    assert cli_args.run_spec == {"key1": "value1"}
    assert cli_args.extra_args == {"key2": "value2"}
