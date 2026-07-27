import rich_click as click
from kiarina.i18n import catalog
from kiarina.utils.app import configure

from kiari.cli.admin.cli import admin
from kiari.cli.batch.cli import batch
from kiari.cli.console.cli import console
from kiari.cli.ext.cli import ext
from kiari.cli.fastapi.cli import fastapi
from kiari.cli.profile.cli import profile
from kiari.cli.schedule.cli import schedule
from kiari.cli.streamlit.cli import streamlit
from kiari.cli.watch.cli import watch

catalog.add_from_package_dir("kiari.resources.i18n")
configure(app_author="kiarina", app_name="kiari")


class KiariGroup(click.RichGroup):
    def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
        if not args and not ctx.resilient_parsing:
            args = ["console"]

        return super().parse_args(ctx, args)

    def resolve_command(
        self, ctx: click.Context, args: list[str]
    ) -> tuple[str | None, click.Command | None, list[str]]:
        if args[0] in self.commands:
            return super().resolve_command(ctx, args)

        if args[0] in {"-l", "--list"}:
            return "profile", profile, ["list", *args[1:]]

        if args[0] in {"-n", "--new"}:
            return "profile", profile, ["new", *args[1:]]

        if args[0] in {"-u", "--use"}:
            return "profile", profile, ["use", *args[1:]]

        if args[0] in {"-w", "--wipe-data"}:
            return "admin", admin, ["wipe-data", *args[1:]]

        if args[0] in {"-c", "--clear-cache"}:
            return "admin", admin, ["clear-cache", *args[1:]]

        try:
            batch_ctx = batch.make_context(
                "batch",
                list(args),
                resilient_parsing=True,
            )

        except click.ClickException:
            batch_ctx = None

        if batch_ctx is not None and batch_ctx.params.get("texts"):
            return "batch", batch, args

        return "console", console, args


@click.group(
    cls=KiariGroup,
    help=("kiari は、クオリアを持つ LLM エージェントの研究・開発・実験を支援する CLI ツールです。"),
    context_settings={
        "help_option_names": ["-h", "--help"],
        "ignore_unknown_options": True,
        "allow_extra_args": True,
    },
    epilog=(
        "[cyan]短縮形:[/cyan]\n\n"
        "kiari -c, --clear-cache    [yellow]admin clear-cache[/yellow]    キャッシュをクリア\n\n"
        "kiari -l, --list           [yellow]profile list[/yellow]         プロファイルの一覧を表示\n\n"
        "kiari -n, --new            [yellow]profile new[/yellow]          新しいプロファイルを作成\n\n"
        "kiari -u, --use            [yellow]profile use[/yellow]          使用するプロファイルを切り替える\n\n"
        "kiari -w, --wipe-data      [yellow]admin wipe-data[/yellow]      データを消去\n\n"
        "kiari <text> ...           [yellow]batch <text> ...[/yellow]     batch モードで実行\n\n"
        "kiari                      [yellow]console[/yellow]              console モードで実行\n\n"
    ),
)
@click.rich_config({"theme": "dracula-modern"})
def kiari() -> None:
    pass


kiari.add_command(admin)
kiari.add_command(profile)
kiari.add_command(batch)
kiari.add_command(console)
kiari.add_command(ext)
kiari.add_command(watch)
kiari.add_command(schedule)
kiari.add_command(fastapi)
kiari.add_command(streamlit)
