from textual.widgets import DataTable, Static


class StatusPanel(Static):
    """Service status panel that polls docker compose ps."""

    def compose(self):
        yield DataTable(id="status-table")

    def on_mount(self) -> None:
        table = self.query_one("#status-table", DataTable)
        table.add_columns("Service", "State", "Health")
        self.refresh_status()
        self.set_interval(3.0, self.refresh_status)

    def refresh_status(self) -> None:
        self.run_worker(self._update_table())

    async def _update_table(self) -> None:
        from cli.core.docker import dc

        table = self.query_one("#status-table", DataTable)
        table.clear()

        try:
            services = dc.ps_parsed()
        except Exception:
            table.add_row("?", "error", "cannot reach docker")
            return

        if not services:
            table.add_row("-", "no services", "-")
            return

        for svc in services:
            name = svc.get("Service", svc.get("Name", "?"))
            state = svc.get("State", "?")
            health = svc.get("Health", svc.get("Status", ""))
            table.add_row(name, state, str(health))
