from cli.core.console import success
from cli.core.docker import dc


def down() -> None:
    """Stop the Odoo development environment."""
    dc.stop()
    success("Environment stopped.")
