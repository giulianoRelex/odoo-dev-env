import typer


def logs(
    service: str = typer.Argument("web", help="Service to view logs for (web, db, or all)."),
    tail: int = typer.Option(100, "--tail", "-n", help="Number of lines to show."),
    no_follow: bool = typer.Option(False, "--no-follow", help="Don't follow log output."),
) -> None:
    """View and follow service logs."""
    from cli.core.docker import dc

    svc = None if service == "all" else service
    dc.logs(service=svc, follow=not no_follow, tail=tail)
