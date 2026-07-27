from typing import Any

from kiari.core.profile import ProfileName

from .._schemas.cli_args import CLIArgs
from .._types.save_mode import SaveMode


def build_cli_args(
    exec_file: str | None = None,
    profile_name: ProfileName | None = None,
    save_mode: SaveMode | None = None,
    extra_args_keys: list[str] | None = None,
    markdown_content_key: str | None = None,
    **kwargs: Any,
) -> CLIArgs:
    run_spec = _normalize_kwargs(kwargs)

    extra_args = {}

    if exec_file:
        file_args: dict[str, Any] | None = None

        if exec_file.endswith(".json"):
            from kiarina.utils.file import read_json_dict

            file_args = read_json_dict(exec_file)

        elif exec_file.endswith(".yaml") or exec_file.endswith(".yml"):
            from kiarina.utils.file import read_yaml_dict

            file_args = read_yaml_dict(exec_file)

        elif exec_file.endswith(".md") or exec_file.endswith(".markdown"):
            from kiarina.utils.file import read_markdown

            if markdown_content := read_markdown(exec_file):
                file_args = markdown_content.metadata

                if markdown_content_key:
                    extra_args[markdown_content_key] = markdown_content.content

        else:  # pragma: no cover
            raise ValueError(f"Unsupported file type: {exec_file}")

        if file_args is None:
            raise FileNotFoundError(f"File not found: {exec_file}")

        run_spec = {**file_args, **run_spec}

    if extra_args_keys:
        for key in extra_args_keys:
            if key in run_spec:
                extra_args[key] = run_spec.pop(key)

    return CLIArgs(
        exec_file=exec_file,
        profile_name=profile_name,
        save_mode=save_mode,
        run_spec=run_spec,
        extra_args=extra_args,
    )


def _normalize_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    return {
        k: v if not isinstance(v, tuple) else list(v)
        for k, v in kwargs.items()
        if v is not None and (not isinstance(v, tuple) or len(v) > 0)
    }
