from datetime import datetime
from pathlib import Path

import typer
from rich.table import Table

from cli.core.config import load_env
from cli.core.console import console, error, info, success, warning
from cli.core.docker import dc
from cli.core.paths import CLI_TEMPLATES_DIR, SNAPSHOTS_DIR

app = typer.Typer(no_args_is_help=True)


def _get_db_info() -> tuple[str, str]:
    env = load_env()
    return env.get("DB_USER", "odoo"), env.get("DB_NAME", "odoo_db")


@app.command()
def snapshot(
    name: str = typer.Argument(..., help="Name for the snapshot."),
) -> None:
    """Create a database snapshot (pg_dump)."""
    db_user, db_name = _get_db_info()
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.dump"
    filepath = SNAPSHOTS_DIR / filename

    info(f"Creating snapshot of '{db_name}'...")
    result = dc.exec_cmd(
        "db",
        ["pg_dump", "-U", db_user, "-d", db_name, "--format=custom"],
        stdin_data=None,
    )

    if result.stdout:
        filepath.write_bytes(result.stdout)
        size_mb = filepath.stat().st_size / (1024 * 1024)
        success(f"Snapshot saved: {filepath.name} ({size_mb:.1f} MB)")
    else:
        error("Snapshot failed — no data received from pg_dump.")
        raise typer.Exit(1)


@app.command()
def restore(
    name: str = typer.Argument(..., help="Snapshot name or prefix to restore."),
) -> None:
    """Restore database from a snapshot."""
    db_user, db_name = _get_db_info()

    # Find snapshot file (exact match or prefix)
    filepath = _find_snapshot(name)
    if not filepath:
        error(f"No snapshot found matching '{name}'.")
        raise typer.Exit(1)

    warning(f"This will REPLACE the database '{db_name}' with snapshot: {filepath.name}")
    confirm = typer.confirm("Continue?", default=False)
    if not confirm:
        info("Operation cancelled.")
        raise typer.Exit()

    info("Stopping web service...")
    dc._run(["stop", "web"])

    info(f"Dropping database '{db_name}'...")
    dc.exec_cmd("db", ["dropdb", "-U", db_user, "--if-exists", db_name])

    info(f"Creating database '{db_name}'...")
    dc.exec_cmd("db", ["createdb", "-U", db_user, db_name])

    info("Restoring from snapshot...")
    dump_data = filepath.read_bytes()
    dc.exec_cmd(
        "db",
        ["pg_restore", "-U", db_user, "-d", db_name, "--no-owner", "--no-acl"],
        stdin_data=dump_data,
    )

    info("Starting web service...")
    dc._run(["start", "web"])

    success(f"Database restored from: {filepath.name}")


@app.command("list")
def list_snapshots() -> None:
    """List available database snapshots."""
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    dumps = sorted(SNAPSHOTS_DIR.glob("*.dump"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not dumps:
        info("No snapshots found.")
        return

    table = Table(title="Database Snapshots")
    table.add_column("Name", style="cyan")
    table.add_column("Date", style="dim")
    table.add_column("Size", justify="right")

    for dump in dumps:
        stat = dump.stat()
        date = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        size_mb = stat.st_size / (1024 * 1024)
        table.add_row(dump.stem, date, f"{size_mb:.1f} MB")

    console.print(table)


@app.command()
def anonymize() -> None:
    """Anonymize personal data in the database."""
    db_user, db_name = _get_db_info()

    warning("This will anonymize partner data and reset user passwords!")
    confirm = typer.confirm("Continue?", default=False)
    if not confirm:
        info("Operation cancelled.")
        raise typer.Exit()

    sql_file = CLI_TEMPLATES_DIR / "anonymize.sql"
    if not sql_file.exists():
        error(f"Anonymization script not found: {sql_file}")
        raise typer.Exit(1)

    sql_data = sql_file.read_bytes()
    info("Running anonymization...")
    dc.exec_cmd("db", ["psql", "-U", db_user, "-d", db_name], stdin_data=sql_data)

    success("Database anonymized. All user passwords set to 'admin'.")


def _find_snapshot(name: str) -> Path | None:
    """Find a snapshot by exact filename, stem match, or prefix."""
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    # Exact match
    exact = SNAPSHOTS_DIR / name
    if exact.exists():
        return exact

    # With .dump extension
    with_ext = SNAPSHOTS_DIR / f"{name}.dump"
    if with_ext.exists():
        return with_ext

    # Prefix match (find newest)
    matches = sorted(
        SNAPSHOTS_DIR.glob(f"{name}*.dump"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return matches[0] if matches else None
