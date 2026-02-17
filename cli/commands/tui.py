def tui() -> None:
    """Launch the interactive TUI dashboard."""
    from cli.tui.app import OdooDevApp

    app = OdooDevApp()
    app.run()
