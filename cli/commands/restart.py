from cli.core.console import info, success
from cli.core.docker import dc


def restart() -> None:
    """Restart the Odoo web container."""
    info("Restarting web service...")
    dc.restart("web")
    success("Web service restarted.")
