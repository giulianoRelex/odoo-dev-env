import typer

from cli.core.config import generate_odoo_conf, load_env
from cli.core.console import error, info, success
from cli.core.docker import dc
from cli.core.paths import CONFIG_DIR, ENV_FILE


def up(
    build: bool = typer.Option(False, "--build", help="Rebuild images before starting."),
    watch: bool = typer.Option(False, "--watch", help="Enable docker compose watch mode."),
) -> None:
    """Start the Odoo development environment."""
    if not ENV_FILE.exists():
        error("No .env file found. Run 'odoodev init' first.")
        raise typer.Exit(1)

    env = load_env()

    # Auto-regenerate odoo.conf if .env is newer
    odoo_conf = CONFIG_DIR / "odoo.conf"
    if not odoo_conf.exists() or ENV_FILE.stat().st_mtime > odoo_conf.stat().st_mtime:
        generate_odoo_conf(env)
        info("Regenerated config/odoo.conf from .env")

    info("Starting environment...")
    dc.up(build=build, watch=watch)

    web_port = env.get("WEB_PORT", "8069")
    pgweb_port = env.get("PGWEB_PORT", "8081")
    success("Environment started!")
    info(f"  Odoo:  http://localhost:{web_port}")
    info(f"  pgweb: http://localhost:{pgweb_port}")
