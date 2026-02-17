from textual.widgets import Static


class ActionsBar(Static):
    """Quick action reference panel."""

    def render(self) -> str:
        return (
            "[bold]Actions[/]\n\n"
            "[cyan]U[/] Up      [cyan]D[/] Down\n"
            "[cyan]R[/] Restart [cyan]S[/] Shell\n"
            "[cyan]C[/] Context [cyan]Q[/] Quit\n"
        )
