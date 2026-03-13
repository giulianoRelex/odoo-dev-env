import typer

from cli.core.config import load_env
from cli.core.console import info, success
from cli.core.docker import dc


def install(
    module: str = typer.Argument(..., help="Module name to install."),
) -> None:
    """Install an Odoo module for the first time and restart the web service."""
    env = load_env()
    db_name = env.get("DB_NAME", "odoo_db")

    info(f"Installing module: {module}")
    dc.exec_cmd("web", ["odoo", "-i", module, "-d", db_name, "--stop-after-init"], interactive=True)

    info("Restarting web service...")
    dc.restart("web")
    success(f"Module '{module}' installed and web service restarted.")
