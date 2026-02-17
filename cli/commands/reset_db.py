import typer

from cli.core.console import info, success, warning
from cli.core.docker import dc


def reset_db() -> None:
    """Destroy the database and volumes, then start fresh."""
    warning("This will DELETE the database and ALL data!")
    confirm = typer.confirm("Are you sure?", default=False)
    if not confirm:
        info("Operation cancelled.")
        raise typer.Exit()

    info("Stopping containers and removing volumes...")
    dc.down(volumes=True)

    info("Starting fresh environment...")
    dc.up()

    success("Database reset complete. Fresh environment is starting.")
