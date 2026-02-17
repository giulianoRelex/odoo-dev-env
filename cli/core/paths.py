from pathlib import Path


def find_project_root(start: Path | None = None) -> Path:
    """Walk up from start (default: cwd) looking for docker-compose.yml."""
    current = start or Path.cwd()
    for directory in [current, *current.parents]:
        if (directory / "docker-compose.yml").exists():
            return directory
    raise FileNotFoundError("Could not find project root (no docker-compose.yml found)")


PROJECT_ROOT = find_project_root()
ADDONS_DIR = PROJECT_ROOT / "addons"
ENTERPRISE_DIR = PROJECT_ROOT / "enterprise"
CONFIG_DIR = PROJECT_ROOT / "config"
SNAPSHOTS_DIR = PROJECT_ROOT / "snapshots"
LOGS_DIR = PROJECT_ROOT / "logs"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
CLI_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
ENV_FILE = PROJECT_ROOT / ".env"
ENV_EXAMPLE = PROJECT_ROOT / ".env.example"
DOCKER_COMPOSE_FILE = PROJECT_ROOT / "docker-compose.yml"
