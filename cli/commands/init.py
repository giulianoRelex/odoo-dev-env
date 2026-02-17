import questionary
import typer

from cli.core.config import generate_odoo_conf, write_env
from cli.core.console import info, success
from cli.core.paths import ADDONS_DIR, CONFIG_DIR, ENTERPRISE_DIR, ENV_FILE, LOGS_DIR, SNAPSHOTS_DIR


def init() -> None:
    """Interactive setup wizard for a new Odoo project."""
    if ENV_FILE.exists():
        overwrite = questionary.confirm(
            ".env file already exists. Overwrite?",
            default=False,
        ).ask()
        if not overwrite:
            raise typer.Exit()

    info("Welcome to the Odoo Dev Environment setup wizard.")

    project_name = questionary.text(
        "Project name:",
        default="my-odoo-project",
        validate=lambda val: len(val.strip()) > 0 or "Project name cannot be empty",
    ).ask()

    odoo_version = questionary.select(
        "Odoo version:",
        choices=["18.0", "17.0", "16.0"],
        default="18.0",
    ).ask()

    web_port = questionary.text("Odoo web port:", default="8069").ask()
    pgweb_port = questionary.text("pgweb port:", default="8081").ask()

    db_name = questionary.text("Database name:", default="odoo_db").ask()
    db_user = questionary.text("Database user:", default="odoo").ask()
    db_password = questionary.text("Database password:", default="odoo").ask()

    language = questionary.text(
        "Default language (e.g. en_US, es_AR, fr_FR):",
        default="en_US",
    ).ask()

    without_demo = questionary.select(
        "Demo data:",
        choices=[
            questionary.Choice("Skip all demo data", value="all"),
            questionary.Choice("Load demo data", value=""),
        ],
        default="all",
    ).ask()

    debugpy = questionary.confirm("Enable debugpy for remote debugging?", default=False).ask()

    admin_password = questionary.text("Admin master password:", default="admin").ask()

    # Build values dict
    odoo_image_tag = odoo_version.replace(".0", "")
    values = {
        "PROJECT_NAME": project_name,
        "ODOO_VERSION": odoo_version,
        "ODOO_IMAGE_TAG": odoo_image_tag,
        "WEB_PORT": web_port,
        "PGWEB_PORT": pgweb_port,
        "DB_NAME": db_name,
        "DB_USER": db_user,
        "DB_PASSWORD": db_password,
        "DB_IMAGE_TAG": "15",
        "DB_PORT": "5432",
        "LOAD_LANGUAGE": language,
        "WITHOUT_DEMO": without_demo,
        "DEBUGPY": "True" if debugpy else "False",
        "DEBUGPY_PORT": "5678",
        "ADMIN_PASSWORD": admin_password,
    }

    # Render files
    write_env(values)
    success(f"Created {ENV_FILE}")

    generate_odoo_conf(values)
    success(f"Created {CONFIG_DIR / 'odoo.conf'}")

    # Ensure directories exist
    for d in [ADDONS_DIR, ENTERPRISE_DIR, SNAPSHOTS_DIR, LOGS_DIR, CONFIG_DIR]:
        d.mkdir(parents=True, exist_ok=True)
        keep = d / ".keep"
        if not keep.exists():
            keep.touch()

    success("Setup complete!")
    info("Next steps:")
    info("  1. odoodev up        # Start the environment")
    info("  2. Open http://localhost:{} in your browser".format(web_port))
