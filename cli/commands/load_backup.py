import subprocess
import tempfile
import zipfile
from pathlib import Path

import typer

from cli.core.config import load_env
from cli.core.console import error, info, success, warning
from cli.core.docker import dc


def load_backup(
    backup: Path = typer.Argument(
        ...,
        help="Path to the Odoo backup (.zip with dump.sql + filestore/).",
        exists=True,
        readable=True,
    ),
    neutralize: bool = typer.Option(
        True,
        help="Neutralize the database (disable crons, mail, etc.).",
    ),
) -> None:
    """Load an Odoo.sh (or Database Manager) backup into the local environment.

    Accepts a .zip file containing a PostgreSQL dump and an optional filestore
    directory.  Drops the current database, restores the dump, copies the
    filestore into the Odoo data volume, and optionally neutralizes the DB so
    it won't send emails or run scheduled actions.
    """
    env = load_env()
    db_user = env.get("DB_USER", "odoo")
    db_name = env.get("DB_NAME", "odoo_db")

    # ── Validate backup ────────────────────────────────────────────
    if not zipfile.is_zipfile(backup):
        error("The file is not a valid .zip archive.")
        raise typer.Exit(1)

    with zipfile.ZipFile(backup) as zf:
        names = zf.namelist()

    # Odoo.sh backups contain dump.sql at root; Database Manager may use
    # dump.sql or a custom-format dump.
    dump_name = None
    for candidate in ("dump.sql", "dump.dump"):
        if candidate in names:
            dump_name = candidate
            break
    if not dump_name:
        error("No dump.sql or dump.dump found inside the .zip.")
        raise typer.Exit(1)

    has_filestore = any(n.startswith("filestore/") for n in names)
    is_custom_format = dump_name.endswith(".dump")

    size_mb = backup.stat().st_size / (1024 * 1024)
    info(f"Backup: {backup.name} ({size_mb:.1f} MB)")
    info(f"  Dump: {dump_name} ({'custom' if is_custom_format else 'SQL'})")
    info(f"  Filestore: {'yes' if has_filestore else 'no'}")

    warning(f"This will REPLACE the database '{db_name}' with the backup contents!")
    if not typer.confirm("Continue?", default=False):
        info("Operation cancelled.")
        raise typer.Exit()

    # ── Extract to temp dir ────────────────────────────────────────
    with tempfile.TemporaryDirectory(prefix="odoodev_backup_") as tmp:
        tmp_path = Path(tmp)
        info("Extracting backup...")
        with zipfile.ZipFile(backup) as zf:
            zf.extractall(tmp_path)

        dump_file = tmp_path / dump_name

        # ── Stop web + pgweb to free DB connections ───────────────
        info("Stopping web and pgweb services...")
        dc._run(["stop", "web", "pgweb"])

        # Terminate any remaining connections to the database
        terminate_sql = (
            f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
            f"WHERE datname = '{db_name}' AND pid <> pg_backend_pid();"
        ).encode()
        dc.exec_cmd(
            "db",
            ["psql", "-U", db_user, "-d", "postgres", "--quiet"],
            stdin_data=terminate_sql,
        )

        info(f"Dropping database '{db_name}'...")
        dc.exec_cmd("db", ["dropdb", "-U", db_user, "--if-exists", db_name])

        info(f"Creating database '{db_name}'...")
        dc.exec_cmd("db", ["createdb", "-U", db_user, "-O", db_user, db_name])

        # ── Restore dump ───────────────────────────────────────────
        info("Restoring database (this may take a while)...")
        dump_data = dump_file.read_bytes()

        if is_custom_format:
            dc.exec_cmd(
                "db",
                [
                    "pg_restore", "-U", db_user, "-d", db_name,
                    "--no-owner", "--no-acl", "--jobs=2",
                ],
                stdin_data=dump_data,
            )
        else:
            dc.exec_cmd(
                "db",
                ["psql", "-U", db_user, "-d", db_name, "--quiet"],
                stdin_data=dump_data,
            )

        success("Database restored.")

        # ── Restore filestore ──────────────────────────────────────
        if has_filestore:
            info("Restoring filestore...")
            filestore_src = tmp_path / "filestore"

            # Start web container briefly so we can docker cp into its volume
            dc._run(["start", "web"])
            container = dc.get_container_name("web")
            if not container:
                warning("Web container not found — skipping filestore copy.")
            else:
                dest = f"/var/lib/odoo/filestore/{db_name}"
                subprocess.run(
                    ["docker", "exec", "--user", "root", container,
                     "rm", "-rf", dest],
                    check=False,
                )
                subprocess.run(
                    ["docker", "cp", str(filestore_src) + "/.",
                     f"{container}:{dest}"],
                    check=True,
                )
                # Fix ownership — must run as root since docker cp
                # creates files owned by the host user
                subprocess.run(
                    ["docker", "exec", "--user", "root", container,
                     "chown", "-R", "odoo:odoo", dest],
                    check=True,
                )
                success("Filestore restored.")
            dc._run(["stop", "web"])
        else:
            info("No filestore in backup — skipping.")

    # ── Neutralize ─────────────────────────────────────────────────
    if neutralize:
        info("Neutralizing database (disabling crons, mail servers, etc.)...")
        dc._run(["start", "web"])
        dc.exec_cmd(
            "web",
            [
                "odoo", "neutralize",
                "--config=/etc/odoo/odoo.conf",
                "-d", db_name,
            ],
            interactive=True,
        )
        success("Database neutralized.")

    # ── Restart everything ─────────────────────────────────────────
    info("Starting services...")
    dc._run(["start", "web", "pgweb"])

    success(f"Backup loaded into '{db_name}'. Access at http://localhost:{env.get('WEB_PORT', '8069')}")
