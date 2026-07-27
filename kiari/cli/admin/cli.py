import rich_click as click

from .clear_cache.cli import clear_cache
from .init.cli import init
from .wipe_data.cli import wipe_data

click.rich_click.USE_RICH_MARKUP = True


@click.group(
    short_help="kiari の初期化や、キャッシュ・データの削除を行うサブコマンドを提供します。",
    help=(
        "kiari の初期化や、キャッシュ・データの削除など、アプリ全体に関わる管理コマンドを提供します。\n\n"
        "---\n\n"
        "> kiari admin init\n\n"
        "Runner 実行時に常に反映される設定ファイルを生成します。\n\n\n"
        "> kiari admin clear-cache\n\n"
        "Runner が生成するキャッシュを全て削除します。\n\n\n"
        "> kiari admin wipe-data\n\n"
        "Runner が生成するデータを全て削除します。\n\n\n"
    ),
    panel="Manage Commands",
)
def admin() -> None:
    """Administrative commands."""


admin.add_command(init)
admin.add_command(clear_cache)
admin.add_command(wipe_data)
