from typing import Optional

import typer

from cli.core.config import load_env
from cli.core.console import info
from cli.core.docker import dc


def test(
    module: str = typer.Argument(..., help="Module name to test, or 'all' to run all tests."),
    log_level: Optional[str] = typer.Option("test", "--log-level", "-l", help="Log level (test, debug, info, warn, error)."),
) -> None:
    """Run tests for a module (or all modules)."""
    env = load_env()
    db_name = env.get("DB_NAME", "odoo_db")

    cmd = [
        "odoo",
        "--test-enable",
        "--stop-after-init",
        "-d", db_name,
        "--http-port=8070",
        f"--log-level={log_level}",
    ]

    if module != "all":
        cmd.extend(["-u", module, "--test-tags", f"/{module}"])
        info(f"Running tests for module: {module}")
    else:
        info("Running all tests (this may take a while)...")

    dc.exec_cmd("web", cmd, interactive=True)
