from kiarina.agi.console_utils import divider, section_header
from kiarina.agi.cost_logger_impl.console import ConsoleCostLogger
from kiarina.agi.cost_record import CostRecord
from rich.console import Group, RenderableType
from rich.text import Text

from kiari.core.rich import console_registry


class DefaultCostLogger(ConsoleCostLogger):
    def log_cost_add(self, cost_record: CostRecord) -> None:
        console_registry.get().print(self._render_cost_add(cost_record))

    def log_cost_flush(self, cost_records: list[CostRecord]) -> None:
        console_registry.get().print(self._render_cost_flush(cost_records))

    def _render_cost_add(self, cost_record: CostRecord) -> RenderableType:
        style = "black"
        cost = self._format_cost(cost_record.microdollars)
        title = f"{cost_record.kind.upper()} COST: {cost}"

        lines = [
            Text(),
            Text(),
            Text(section_header(title), style=style),
            Text(f"kind: {cost_record.kind}", style=style),
            Text(f"source: {cost_record.source}", style=style),
        ]

        for key, value in cost_record.metadata.items():
            if value:
                lines.append(Text(f"{key}: {value}", style=style))

        lines.append(Text(divider(), style=style))

        return Group(*lines)

    def _render_cost_flush(self, cost_records: list[CostRecord]) -> RenderableType:
        style = "black"
        total_cost = self._format_cost(
            sum(record.microdollars for record in cost_records),
        )
        title = f"TOTAL COSTS: {total_cost}"

        renderables: list[RenderableType] = [
            Text(),
            Text(),
            Text(section_header(title), style=style),
        ]

        for kind, source_map in self._aggregate(cost_records).items():
            renderables.append(Text(kind, style=style))

            for source, aggregates in source_map.items():
                renderables.append(
                    Text(
                        f"  {source}: {aggregates.count} calls, {self._format_cost(aggregates.total_cost)}",
                        style=style,
                    )
                )

        renderables.append(Text(divider(), style=style))
        return Group(*renderables)
