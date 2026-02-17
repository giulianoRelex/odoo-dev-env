from rich.console import Console

console = Console()


def success(message: str) -> None:
    console.print(f"[bold green]✓[/] {message}")


def error(message: str) -> None:
    console.print(f"[bold red]✗[/] {message}")


def warning(message: str) -> None:
    console.print(f"[bold yellow]![/] {message}")


def info(message: str) -> None:
    console.print(f"[bold blue]ℹ[/] {message}")
