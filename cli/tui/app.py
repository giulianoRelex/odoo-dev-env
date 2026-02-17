from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import Footer, Header

from cli.core.config import load_env
from cli.tui.widgets.actions_bar import ActionsBar
from cli.tui.widgets.log_viewer import LogViewer
from cli.tui.widgets.status_panel import StatusPanel


class OdooDevApp(App):
    """Textual TUI for Odoo development environment."""

    CSS_PATH = "styles/app.tcss"

    TITLE = "odoodev"
    SUB_TITLE = "Odoo Development Environment"

    BINDINGS = [
        Binding("u", "action_up", "Up", show=True),
        Binding("d", "action_down", "Down", show=True),
        Binding("r", "action_restart", "Restart", show=True),
        Binding("s", "action_shell", "Shell", show=True),
        Binding("c", "action_context", "Context", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    def compose(self) -> ComposeResult:
        env = load_env()
        project = env.get("PROJECT_NAME", "odoo-project")
        version = env.get("ODOO_VERSION", "18.0")

        yield Header()
        yield Horizontal(
            StatusPanel(id="status-panel"),
            ActionsBar(id="actions-bar"),
            id="top-row",
        )
        yield Container(
            LogViewer(id="log-viewer"),
            id="bottom-row",
        )
        yield Footer()

        self.title = f"odoodev — {project}"
        self.sub_title = f"Odoo {version}"

    def action_up(self) -> None:
        self._run_docker_action("up")

    def action_down(self) -> None:
        self._run_docker_action("down")

    def action_restart(self) -> None:
        self._run_docker_action("restart")

    def action_shell(self) -> None:
        self.app.exit(return_code=42)  # Signal to spawn shell externally

    def action_context(self) -> None:
        self._run_docker_action("context")

    def _run_docker_action(self, action: str) -> None:
        self.run_worker(self._docker_worker(action))

    async def _docker_worker(self, action: str) -> None:
        from cli.core.docker import dc

        status_panel = self.query_one("#status-panel", StatusPanel)

        match action:
            case "up":
                dc.up()
            case "down":
                dc.stop()
            case "restart":
                dc.restart("web")
            case "context":
                from cli.commands.context import context

                context()

        status_panel.refresh_status()
