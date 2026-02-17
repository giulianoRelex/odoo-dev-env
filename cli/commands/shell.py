from cli.core.console import info
from cli.core.docker import dc


def shell() -> None:
    """Open a bash shell inside the Odoo container."""
    info("Entering Odoo container shell...")
    dc.exec_cmd("web", ["/bin/bash"], interactive=True)
