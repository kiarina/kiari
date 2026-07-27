import hashlib
import importlib.util
import logging
import sys
from pathlib import Path

from kiarina.i18n import get_i18n, get_system_language

from kiari.core.rich import console_registry, render_status_block

from .._i18n import PluginI18n
from .._settings import settings_manager

logger = logging.getLogger(__name__)


async def load_plugin(file_path: str) -> None:
    module_name = _to_module_name(file_path)

    if module_name in sys.modules:
        return

    spec = importlib.util.spec_from_file_location(module_name, file_path)

    if spec is None or spec.loader is None:  # pragma: no cover
        raise ImportError(f"Cannot load plugin module from {file_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module

    try:
        spec.loader.exec_module(module)

    except ImportError as e:
        _handle_import_error(e)
        raise


def _to_module_name(file_path: str) -> str:
    settings = settings_manager.get_settings()

    resolved_path = str(Path(file_path).resolve())
    path_hash = hashlib.sha256(resolved_path.encode()).hexdigest()[:16]
    return f"{settings.module_prefix}.{path_hash}"


def _handle_import_error(e: ImportError) -> None:
    t = get_i18n(PluginI18n, get_system_language())

    missing = str(e).split("'")[1] if "'" in str(e) else "unknown"

    console_registry.get().print(
        render_status_block(
            title=t.missing_dependency_title.format(missing=missing),
            lines=[
                f"[blue]{t.please_install}[/blue]",
                f"[green]  {t.install_command.format(missing=missing)}[/green]",
            ],
            status="warning",
        )
    )
