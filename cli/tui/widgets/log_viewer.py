import asyncio
import subprocess

from textual.widgets import RichLog, Static


class LogViewer(Static):
    """Live log viewer that streams docker compose logs."""

    def compose(self):
        yield RichLog(id="rich-log", highlight=True, markup=True, wrap=True)

    def on_mount(self) -> None:
        self._process: subprocess.Popen | None = None
        self.run_worker(self._stream_logs())

    async def _stream_logs(self) -> None:
        from cli.core.paths import PROJECT_ROOT

        rich_log = self.query_one("#rich-log", RichLog)

        try:
            self._process = subprocess.Popen(
                ["docker", "compose", "logs", "-f", "--tail", "50", "web"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=PROJECT_ROOT,
            )
        except FileNotFoundError:
            rich_log.write("[red]docker compose not found[/]")
            return

        loop = asyncio.get_event_loop()
        while self._process and self._process.poll() is None:
            line = await loop.run_in_executor(None, self._process.stdout.readline)
            if line:
                text = line.decode("utf-8", errors="replace").rstrip()
                rich_log.write(text)
            else:
                await asyncio.sleep(0.1)

    def on_unmount(self) -> None:
        if self._process and self._process.poll() is None:
            self._process.terminate()
