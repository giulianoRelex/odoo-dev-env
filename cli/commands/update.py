import typer

from cli.core.config import load_env
from cli.core.console import info, success
from cli.core.docker import dc


def update(
    module: str = typer.Argument(..., help="Module name to update."),
) -> None:
    """Update (upgrade) an Odoo module and restart the web service."""
    env = load_env()
    db_name = env.get("DB_NAME", "odoo_db")

    info(f"Updating module: {module}")
    dc.exec_cmd("web", ["odoo", "-u", module, "-d", db_name, "--stop-after-init"], interactive=True)

    info("Restarting web service...")
    dc.restart("web")
    success(f"Module '{module}' updated and web service restarted.")
