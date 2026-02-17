# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Generic, reusable Dockerized Odoo development environment boilerplate. Three services run via Docker Compose: Odoo web (`web`), PostgreSQL (`db`), and pgweb (`pgweb` — a DB browser UI).

Custom modules go in `addons/` (mounted at `/mnt/extra-addons`). Enterprise modules go in `enterprise/` (mounted at `/mnt/enterprise-addons`). Both directories are gitignored and created at runtime.

The project is managed via the `odoodev` Python CLI (installed from `pyproject.toml`). Odoo runs in dev mode (`--dev=reload,xml`) for hot-reload.

## Essential Commands

All operations go through the `odoodev` CLI. Requires a `.env` file (run `odoodev init` or copy `.env.example`).

```bash
# First-time setup
pip install -e .                 # Install the CLI
odoodev init                     # Interactive setup wizard

# Environment lifecycle
odoodev up [--build] [--watch]   # Start services (docker compose up -d)
odoodev down                     # Stop services
odoodev restart                  # Restart only the Odoo web container
odoodev status                   # Show service status table
odoodev reset-db                 # Destroy DB + volumes, fresh start

# Development
odoodev shell                    # Bash shell inside the Odoo container
odoodev scaffold <name>          # Create new module from template in addons/
odoodev update <module>          # odoo -u <module> then restart web
odoodev logs [web|db|all]        # Follow service logs

# Testing
odoodev test <module>            # Run tests for a single module
odoodev test all                 # Run all tests

# Database operations
odoodev db snapshot <name>       # pg_dump to snapshots/
odoodev db restore <name>        # Restore from snapshot
odoodev db list                  # List available snapshots
odoodev db anonymize             # Replace personal data with fake data

# AI Agent support
odoodev context                  # Generate PROJECT_CONTEXT.md from addons/

# TUI dashboard
odoodev tui                      # Launch interactive terminal dashboard
```

Under the hood, tests run:
```bash
docker compose exec web odoo --test-enable --stop-after-init -d $DB_NAME --test-tags=/<module> --http-port=8070 --log-level=test
```

## Pre-commit Hooks

Configured in `.pre-commit-config.yaml`. Runs automatically on commit:
- **ruff**: Python linting + formatting (auto-fix enabled)
- **pylint-odoo**: Odoo-specific linting (config in `pyproject.toml`)
- **eslint**: JS and XML linting (with `eslint-plugin-owl`, config in `.eslintrc.json`)
- Standard hooks: trailing whitespace, end-of-file fixer, YAML check, large file check

## Architecture

```
cli/                            # Python CLI package (odoodev)
│   ├── main.py                 # Typer app entry point
│   ├── commands/               # One file per command (init, up, down, etc.)
│   ├── core/                   # Shared utilities (docker, config, paths, console)
│   ├── tui/                    # Textual TUI dashboard
│   └── templates/              # Jinja2 templates (odoo.conf, .env, SQL, context)
│
docker-compose.yml              # Service definitions (web, db, pgweb)
entrypoint.sh                   # Container entrypoint: debugpy, language loading, dev mode
config/                         # Runtime config (odoo.conf generated here)
.env / .env.example             # Environment variables (ports, DB creds, language, debug)
templates/module_template/      # Boilerplate for scaffolding new Odoo modules
addons/                         # Custom modules (gitignored, mounted into container)
enterprise/                     # Enterprise modules (gitignored, mounted into container)
snapshots/                      # Database snapshots (gitignored)
logs/                           # Shared log directory for Odoo and PostgreSQL
.devcontainer/                  # VS Code Dev Container config
pyproject.toml                  # CLI packaging + ruff/pylint tool config
```

### Key Environment Variables (.env)

| Variable | Default | Purpose |
|---|---|---|
| `PROJECT_NAME` | `my-odoo-project` | Project identifier |
| `COMPOSE_PROJECT_NAME` | `my-odoo-project` | Docker container naming prefix |
| `ODOO_VERSION` | `18.0` | Odoo version |
| `DEBUGPY` | `False` | Set to `True` to enable debugpy |
| `DEBUGPY_PORT` | `5678` | Host port for debugpy |
| `LOAD_LANGUAGE` | `en_US` | Language to auto-install on first run |
| `INIT_MODULES` | (empty) | Comma-separated modules to install at startup |
| `WEB_PORT` | `8069` | Host port for Odoo web |
| `PGWEB_PORT` | `8081` | Host port for pgweb DB browser |

### Container Access Points

- Odoo web: `http://localhost:${WEB_PORT}` (default 8069)
- pgweb DB browser: `http://localhost:${PGWEB_PORT}` (default 8081)
- debugpy: port `${DEBUGPY_PORT}` (default 5678, when `DEBUGPY=True`)

## Odoo Module Development

Modules follow standard Odoo 18 structure: `__manifest__.py`, `models/`, `views/`, `security/`, `tests/`. The scaffold template in `templates/module_template/` provides a working starting point with an example model, views, ACLs, and a test case.

```bash
odoodev scaffold my_module       # Creates addons/my_module/ from template
odoodev update my_module         # Apply Python/data changes
odoodev test my_module           # Run module tests
```

After modifying a module's Python models or data files, run `odoodev update <name>` to apply changes. XML/JS changes are picked up automatically via dev mode hot-reload.
