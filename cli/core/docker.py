import json
import shutil
import subprocess
import sys

from cli.core.paths import PROJECT_ROOT


class DockerCompose:
    """Wrapper around docker compose commands."""

    def __init__(self) -> None:
        self._cmd = self._detect_command()

    @staticmethod
    def _detect_command() -> list[str]:
        """Detect whether to use 'docker compose' or 'docker-compose'."""
        if shutil.which("docker"):
            result = subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return ["docker", "compose"]
        if shutil.which("docker-compose"):
            return ["docker-compose"]
        raise RuntimeError("Neither 'docker compose' nor 'docker-compose' found. Please install Docker.")

    def _run(
        self,
        args: list[str],
        capture: bool = False,
        check: bool = True,
        input_data: bytes | None = None,
    ) -> subprocess.CompletedProcess:
        cmd = [*self._cmd, *args]
        return subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=capture,
            check=check,
            input=input_data,
        )

    def _exec(
        self,
        args: list[str],
        interactive: bool = False,
    ) -> subprocess.CompletedProcess:
        """Run a command, optionally replacing the current process for interactive use."""
        cmd = [*self._cmd, *args]
        if interactive:
            sys.stdout.flush()
            sys.stderr.flush()
            return subprocess.run(cmd, cwd=PROJECT_ROOT)
        return subprocess.run(cmd, cwd=PROJECT_ROOT, check=True)

    def up(self, build: bool = False, watch: bool = False) -> None:
        args = ["up", "-d"]
        if build:
            args.append("--build")
        if watch:
            args.append("--watch")
        self._run(args)

    def down(self, volumes: bool = False) -> None:
        args = ["down"]
        if volumes:
            args.append("-v")
        self._run(args)

    def stop(self) -> None:
        self._run(["stop"])

    def restart(self, service: str = "web") -> None:
        self._run(["restart", service])

    def ps(self, format_json: bool = False) -> str:
        args = ["ps"]
        if format_json:
            args.extend(["--format", "json"])
        result = self._run(args, capture=True)
        return result.stdout.decode() if result.stdout else ""

    def ps_parsed(self) -> list[dict]:
        """Return parsed service status as list of dicts."""
        raw = self.ps(format_json=True).strip()
        if not raw:
            return []
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # docker compose may output one JSON object per line
            results = []
            for line in raw.splitlines():
                line = line.strip()
                if line:
                    try:
                        results.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            return results

    def logs(self, service: str | None = None, follow: bool = True, tail: int = 100) -> None:
        args = ["logs"]
        if follow:
            args.append("-f")
        args.extend(["--tail", str(tail)])
        if service:
            args.append(service)
        self._exec(args, interactive=True)

    def exec_cmd(
        self,
        service: str,
        command: list[str],
        interactive: bool = False,
        stdin_data: bytes | None = None,
    ) -> subprocess.CompletedProcess:
        args = ["exec"]
        if stdin_data is not None:
            args.append("-T")
        args.extend([service, *command])
        if interactive:
            return self._exec(args, interactive=True)
        return self._run(args, capture=True, input_data=stdin_data)

    def get_container_name(self, service: str) -> str | None:
        """Dynamically look up the container name for a service."""
        result = self._run(["ps", "-q", service], capture=True, check=False)
        container_id = result.stdout.decode().strip() if result.stdout else ""
        if not container_id:
            return None
        inspect = subprocess.run(
            ["docker", "inspect", "--format", "{{.Name}}", container_id],
            capture_output=True,
            text=True,
        )
        return inspect.stdout.strip().lstrip("/") if inspect.returncode == 0 else None


dc = DockerCompose()
