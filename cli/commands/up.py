import os
import stat

import typer

from cli.core.config import generate_odoo_conf, load_env
from cli.core.console import error, info, success
from cli.core.docker import dc
from cli.core.paths import CONFIG_DIR, ENV_FILE, LOGS_DIR


def _ensure_logs_dir() -> None:
    """Ensure the logs directory exists and is writable by container processes."""
    LOGS_DIR.mkdir(exist_ok=True)
    current = LOGS_DIR.stat().st_mode
    desired = current | stat.S_IWOTH | stat.S_IXOTH  # o+wx
    if current != desired:
        os.chmod(LOGS_DIR, desired)


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

    _ensure_logs_dir()
    info("Starting environment...")
    dc.up(build=build, watch=watch)

    web_port = env.get("WEB_PORT", "8069")
    pgweb_port = env.get("PGWEB_PORT", "8081")
    success("Environment started!")
    info(f"  Odoo:  http://localhost:{web_port}")
    info(f"  pgweb: http://localhost:{pgweb_port}")
