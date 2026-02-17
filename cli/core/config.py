from pathlib import Path

from dotenv import dotenv_values
from jinja2 import Environment, FileSystemLoader

from cli.core.paths import CLI_TEMPLATES_DIR, CONFIG_DIR, ENV_FILE


def load_env(env_file: Path | None = None) -> dict[str, str | None]:
    """Read .env file and return values as a dict."""
    path = env_file or ENV_FILE
    if not path.exists():
        return {}
    return dict(dotenv_values(path))


def _get_jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(CLI_TEMPLATES_DIR)),
        keep_trailing_newline=True,
    )


def write_env(values: dict[str, str], dest: Path | None = None) -> Path:
    """Render env.j2 template with values and write to .env."""
    env = _get_jinja_env()
    template = env.get_template("env.j2")
    output = template.render(**values)
    target = dest or ENV_FILE
    target.write_text(output)
    return target


def generate_odoo_conf(env_values: dict[str, str | None] | None = None) -> Path:
    """Render odoo.conf.j2 template and write to config/odoo.conf."""
    if env_values is None:
        env_values = load_env()
    jinja_env = _get_jinja_env()
    template = jinja_env.get_template("odoo.conf.j2")
    output = template.render(**{k: v for k, v in env_values.items() if v is not None})
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    target = CONFIG_DIR / "odoo.conf"
    target.write_text(output)
    return target
