import typer

from cli.commands import context, db, down, init, load_backup, logs, reset_db, restart, scaffold, shell, status, test, tui, up, update

app = typer.Typer(
    name="odoodev",
    help="CLI for Odoo development environment management.",
    no_args_is_help=True,
)

app.command()(init.init)
app.command()(up.up)
app.command()(down.down)
app.command()(restart.restart)
app.command()(status.status)
app.command()(logs.logs)
app.command()(shell.shell)
app.command()(test.test)
app.command()(scaffold.scaffold)
app.command()(update.update)
app.command("reset-db")(reset_db.reset_db)
app.command("load-backup")(load_backup.load_backup)
app.command()(context.context)
app.command()(tui.tui)
app.add_typer(db.app, name="db", help="Database snapshot, restore, list, and anonymize.")

if __name__ == "__main__":
    app()
