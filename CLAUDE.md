# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Generic, reusable Dockerized Odoo development environment boilerplate. Requires Python 3.10+ and Docker Compose v2. Three services run via Docker Compose: Odoo web (`web`), PostgreSQL with pgvector (`db`), and pgweb (`pgweb` — a DB browser UI). Services have health checks: `db` uses `pg_isready`, `web` hits `/web/health`.

Custom modules go in `addons/` (mounted at `/mnt/extra-addons`). Enterprise modules go in `enterprise/` (mounted at `/mnt/enterprise-addons`). Both directories are gitignored and created at runtime.

The project is managed via the `odoodev` Python CLI (installed from `pyproject.toml`). Odoo runs in dev mode (`--dev=reload,xml`) for hot-reload.

Default stack: **Odoo 19** + **PostgreSQL 16 (pgvector)**.

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
odoodev addon-install <module>   # Install a single module and restart
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
odoodev load-backup <path>       # Load Odoo.sh or DB Manager backup (auto-neutralizes)

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
- **ruff**: Python linting + formatting (auto-fix enabled, line-length 120)
- **pylint-odoo**: Odoo-specific linting (config in `pyproject.toml`)
- **eslint**: JS and XML linting (with `eslint-plugin-owl`, config in `.eslintrc.json`)
- Standard hooks: trailing whitespace, end-of-file fixer, YAML check, large file check

Run manually: `pre-commit run --all-files`

## Architecture

```
cli/                            # Python CLI package (odoodev)
│   ├── main.py                 # Typer app entry point, registers all commands
│   ├── commands/               # One file per command (init, up, down, etc.)
│   ├── core/                   # Shared utilities
│   │   ├── docker.py           # DockerCompose wrapper (auto-detects v1/v2)
│   │   ├── config.py           # Jinja2 template rendering for .env and odoo.conf
│   │   ├── paths.py            # Project root detection (walks up looking for docker-compose.yml)
│   │   └── console.py          # Rich-based styled output (success/error/warning/info)
│   ├── tui/                    # Textual TUI dashboard
│   └── templates/              # Jinja2 templates (odoo.conf, .env, SQL, context)
│
docker-compose.yml              # Service definitions (web, db, pgweb)
entrypoint.sh                   # Container entrypoint: debugpy, language loading, dev mode
config/                         # Runtime config (odoo.conf generated here)
.env / .env.example             # Environment variables (ports, DB creds, language, debug)
templates/module_template/      # Boilerplate for scaffolding new Odoo modules
skills/odoo-19.0/               # Odoo 19 development knowledge base (18 reference guides)
addons/                         # Custom modules (gitignored, mounted into container)
enterprise/                     # Enterprise modules (gitignored, mounted into container)
snapshots/                      # Database snapshots (gitignored)
logs/                           # Shared log directory for Odoo and PostgreSQL
.devcontainer/                  # VS Code Dev Container config
pyproject.toml                  # CLI packaging + ruff/pylint tool config
```

### CLI Internals

- **Command pattern**: Each command is a function decorated with `@app.command()` in its own file under `cli/commands/`. The `db` commands use a Typer subapp (`db_app = typer.Typer()`) registered via `app.add_typer()`.
- **Docker abstraction**: `DockerCompose` class wraps all docker compose calls, auto-detecting v1 (`docker-compose`) vs v2 (`docker compose`). Supports streaming (interactive) and captured output modes.
- **Project root**: `find_project_root()` walks up from CWD to find `docker-compose.yml`, so commands work from any subdirectory.
- **Config auto-regeneration**: `odoodev up` regenerates `config/odoo.conf` from the Jinja2 template if `.env` is newer than the existing config. No manual config editing needed.
- **Error handling**: Commands use `raise typer.Exit(1)` for errors and `console.error()` / `console.success()` for styled output.

### Implicit Runtime Behaviors

- **Addon dependency auto-install**: `entrypoint.sh` scans addon directories (up to 3 levels deep) for `requirements.txt` files and installs them via pip before Odoo starts.
- **Docker Compose watch mode**: `odoodev up --watch` enables file syncing — changes in `./addons` are automatically synced to `/mnt/extra-addons` in the container.
- **Language check**: The entrypoint uses psycopg2 to check if a language is already loaded in the DB before attempting to install it, avoiding redundant loads.
- **Module scaffolding**: The `scaffold` command copies `templates/module_template/` and replaces the `__module_name__` placeholder in both filenames and file contents.
- **Log duplication**: Odoo output is tee'd to `/var/log/odoo/odoo.log` (mapped to `logs/` on the host) in addition to stdout.
- **Debugpy**: When `DEBUGPY=True`, the entrypoint installs debugpy and launches Odoo under `python -m debugpy --listen 0.0.0.0:5678`. Attach VS Code's debugger to `localhost:${DEBUGPY_PORT}`.
- **DB operations**: `db restore` and `load-backup` stop the web service during the operation, then restart it. Snapshots use pg custom format (`--format=custom`), restores skip ownership (`--no-owner --no-acl`).
- **Backup loading**: `load-backup` accepts Odoo.sh or Database Manager `.zip` backups containing `dump.sql` (or `dump.dump` custom format) and an optional `filestore/` directory. It drops the current DB, restores the dump, copies the filestore into the Odoo data volume, and optionally neutralizes the DB (disabling crons, mail servers, etc.).

### Key Environment Variables (.env)

| Variable | Default | Purpose |
|---|---|---|
| `PROJECT_NAME` | `my-odoo-project` | Project identifier |
| `COMPOSE_PROJECT_NAME` | `my-odoo-project` | Docker container naming prefix |
| `ODOO_VERSION` | `19.0` | Odoo version |
| `ODOO_IMAGE` | `odoo:19` | Docker image for Odoo |
| `DB_IMAGE` | `pgvector/pgvector:pg16` | Docker image for PostgreSQL (with pgvector) |
| `DEBUGPY` | `False` | Set to `True` to enable debugpy |
| `DEBUGPY_PORT` | `5678` | Host port for debugpy |
| `LOAD_LANGUAGE` | `en_US` | Language to auto-install on first run |
| `INIT_MODULES` | (empty) | Comma-separated modules to install at startup |
| `WITHOUT_DEMO` | `all` | Skip demo data (`all` to skip all) |
| `WEB_PORT` | `8069` | Host port for Odoo web |
| `PGWEB_PORT` | `8081` | Host port for pgweb DB browser |
| `DB_NAME` | `odoo_db` | PostgreSQL database name |
| `DB_USER` | `odoo` | PostgreSQL user |
| `DB_PASSWORD` | `odoo` | PostgreSQL password |
| `ADMIN_PASSWORD` | `admin` | Odoo master admin password |

### Container Access Points

- Odoo web: `http://localhost:${WEB_PORT}` (default 8069)
- pgweb DB browser: `http://localhost:${PGWEB_PORT}` (default 8081)
- debugpy: port `${DEBUGPY_PORT}` (default 5678, when `DEBUGPY=True`)

## Odoo Module Development

Modules follow standard Odoo structure: `__manifest__.py`, `models/`, `views/`, `security/`, `tests/`. The scaffold template in `templates/module_template/` provides a working starting point with an example model, views, ACLs, and a test case.

```bash
odoodev scaffold my_module       # Creates addons/my_module/ from template
odoodev addon-install my_module  # Install the module for the first time
odoodev update my_module         # Apply Python/data changes after edits
odoodev test my_module           # Run module tests
```

**When to restart vs hot-reload:**
- **Automatic** (dev mode): XML view changes, QWeb templates, JS/CSS assets
- **Requires `odoodev update <name>`**: Python model changes (new fields, method changes), security CSV, data XML files
- **Requires `odoodev reset-db`**: Removing fields/models, major structural changes

### Odoo 19 Development Knowledge

The `skills/odoo-19.0/` directory contains 18 specialized reference guides for Odoo 19 development. Consult these before implementing Odoo-specific code.

| Topic | Guide | When to Use |
|---|---|---|
| Actions | `skills/odoo-19.0/references/odoo-19-actions-guide.md` | Actions, menus, cron jobs, server actions |
| API Decorators | `skills/odoo-19.0/references/odoo-19-decorator-guide.md` | @api decorators, compute fields, validation |
| Controllers | `skills/odoo-19.0/references/odoo-19-controller-guide.md` | HTTP endpoints, routes, web controllers |
| Data Files | `skills/odoo-19.0/references/odoo-19-data-guide.md` | XML/CSV data files, records, shortcuts |
| Development | `skills/odoo-19.0/references/odoo-19-development-guide.md` | Module creation, manifest, wizards, reports |
| Field Types | `skills/odoo-19.0/references/odoo-19-field-guide.md` | Model field types and parameters |
| Manifest | `skills/odoo-19.0/references/odoo-19-manifest-guide.md` | `__manifest__.py` configuration |
| Migration | `skills/odoo-19.0/references/odoo-19-migration-guide.md` | Migration scripts, pre/post/end hooks |
| Mixins | `skills/odoo-19.0/references/odoo-19-mixins-guide.md` | mail.thread, activities, email aliases |
| Model Methods | `skills/odoo-19.0/references/odoo-19-model-guide.md` | ORM, CRUD, search, domain filters |
| OWL Components | `skills/odoo-19.0/references/odoo-19-owl-guide.md` | OWL UI components, hooks, services |
| Performance | `skills/odoo-19.0/references/odoo-19-performance-guide.md` | Query optimization, N+1 prevention |
| Reports | `skills/odoo-19.0/references/odoo-19-reports-guide.md` | QWeb reports, PDF/HTML, paper formats |
| Security | `skills/odoo-19.0/references/odoo-19-security-guide.md` | ACL, record rules, field permissions |
| Testing | `skills/odoo-19.0/references/odoo-19-testing-guide.md` | TransactionCase, HttpCase, mocking |
| Transactions | `skills/odoo-19.0/references/odoo-19-transaction-guide.md` | Savepoints, UniqueViolation, errors |
| Translation | `skills/odoo-19.0/references/odoo-19-translation-guide.md` | i18n, PO files, translatable fields |
| Views & XML | `skills/odoo-19.0/references/odoo-19-view-guide.md` | XML views, kanban, xpath, QWeb templates |

**Key Odoo 19 changes from prior versions:**
- `<tree>` tag replaced by `<list>`
- `attrs` removed — use `invisible=`, `readonly=`, `required=` directly
- `@api.ondelete` for delete validation instead of overriding `unlink()`
- `_sql_constraints` replaced by `models.Constraint(...)`
- `read_group()` replaced by `_read_group()`
- `t-esc` deprecated in favor of `t-out`
- `category_id` on `res.groups` replaced by `privilege_id`
- `@api.private` decorator for non-RPC methods
- CamelCase class names auto-derive `_name`
- Kanban templates use `t-name="card"` instead of `t-name="kanban-box"`

## MCP Tools

Five MCP servers are configured in `.mcp.json` (gitignored — copy from `.mcp.json.example`):

| Server | Package | Capability |
|---|---|---|
| `postgres` | `@modelcontextprotocol/server-postgres` | Query the live Odoo DB directly |
| `filesystem` | `@modelcontextprotocol/server-filesystem` | Read/write project files |
| `fetch` | `@modelcontextprotocol/server-fetch` | Fetch Odoo docs and web pages |
| `context7` | `@upstash/context7-mcp@latest` | Up-to-date library docs (Odoo, Python, JS) |
| `memory` | `@modelcontextprotocol/server-memory` | Persistent cross-session memory |

Setup: `cp .mcp.json.example .mcp.json`, edit DB credentials and absolute paths, then restart Claude Code. The `postgres` server requires the DB container to be running (`odoodev up`).

## Devlog Convention

Each addon module under development maintains a `docs/devlog-faseN.md` file per development phase. These devlogs track:
- Technical decisions made and their rationale
- Deferred work and why
- Files created/modified in the phase

When starting work on a module phase, check existing devlogs for context. When finishing, update the devlog with decisions and outcomes.
