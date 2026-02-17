from rich.table import Table

from cli.core.console import console
from cli.core.docker import dc


def status() -> None:
    """Show status of all services."""
    services = dc.ps_parsed()
    if not services:
        console.print("[dim]No services running.[/]")
        return

    table = Table(title="Services")
    table.add_column("Service", style="cyan")
    table.add_column("State", style="bold")
    table.add_column("Status")
    table.add_column("Ports", style="dim")

    for svc in services:
        name = svc.get("Service", svc.get("Name", "?"))
        state = svc.get("State", "?")
        health = svc.get("Health", svc.get("Status", ""))
        ports = svc.get("Ports", svc.get("Publishers", ""))
        if isinstance(ports, list):
            ports = ", ".join(
                f"{p.get('PublishedPort', '?')}:{p.get('TargetPort', '?')}"
                for p in ports
                if p.get("PublishedPort")
            )

        state_style = "green" if state == "running" else "red" if state == "exited" else "yellow"
        table.add_row(name, f"[{state_style}]{state}[/]", str(health), str(ports))

    console.print(table)
