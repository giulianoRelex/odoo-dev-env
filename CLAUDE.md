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

## MCP Tools

Five MCP servers are configured in `.mcp.json` (gitignored — copy from `.mcp.json.example`):

| Server | Package | Capability |
|---|---|---|
| `postgres` | `@modelcontextprotocol/server-postgres` | Query the live Odoo DB directly |
| `filesystem` | `@modelcontextprotocol/server-filesystem` | Read/write project files |
| `fetch` | `@modelcontextprotocol/server-fetch` | Fetch Odoo docs and web pages |
| `context7` | `@upstash/context7-mcp@latest` | Up-to-date library docs (Odoo, Python, JS) |
| `memory` | `@modelcontextprotocol/server-memory` | Persistent cross-session memory |

### Setup

```bash
cp .mcp.json.example .mcp.json
# Edit .mcp.json: replace DB credentials and /absolute/path/to/project
# Then restart Claude Code — run /mcp to verify all 5 servers are connected
```

The `postgres` server requires the DB container to be running (`odoodev up`).
Memory is stored in `.claude/memory.json` (gitignored via `.claude/`).

### Useful postgres MCP queries

```sql
-- List all custom tables
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- Inspect a model's columns
SELECT column_name, data_type FROM information_schema.columns
WHERE table_name = 'my_model' ORDER BY ordinal_position;

-- Check installed modules
SELECT name, state FROM ir_module_module WHERE state = 'installed' ORDER BY name;

-- Recent log entries
SELECT create_date, type, name, res_id FROM mail_message ORDER BY create_date DESC LIMIT 20;
```

### Memory MCP usage

Use the memory server to persist context across sessions:

```
# Save important project decisions
remember: "We use res.partner inheritance for customer extensions, not a separate model"

# Recall at start of new session
recall project decisions
```

## AI Agent Workflow

### Session start checklist

Run these two commands at the start of every AI session to load fresh context:

```bash
odoodev context    # Regenerates PROJECT_CONTEXT.md from addons/
odoodev status     # Shows which containers are running
```

Then share `PROJECT_CONTEXT.md` with Claude Code: `cat PROJECT_CONTEXT.md`.

### Structured prompts for common tasks

**Adding a field to an existing model:**
```
Context: [paste PROJECT_CONTEXT.md section for the module]
Task: Add a `delivery_notes` (Text) field to `sale.order` in module `my_sale_ext`.
Constraints: Odoo 18, follow existing code style, add the field to the form view.
```

**Creating a new model from scratch:**
```
Context: [paste PROJECT_CONTEXT.md]
Task: Create model `my.shipment` in module `my_logistics` with fields: name (Char, required),
      partner_id (Many2one res.partner), state (Selection: draft/confirmed/done).
      Include form + list views, ACLs for group_user, and a basic test.
```

**Debugging an error:**
```
Error: [paste full traceback]
Context: [paste relevant model/view code]
Check ERRORS.md first. Then diagnose root cause and propose minimal fix.
```

**Writing tests:**
```
Context: [paste model code]
Task: Write TransactionCase tests for `my.model` covering: create, write, unlink,
      and the `action_confirm` method. Use realistic test data.
```

### Odoo 18 anti-patterns to avoid

1. **`attrs` / `states` in views** — use `invisible=`, `readonly=`, `required=` directly
2. **`@api.multi`** — removed; all methods operate on recordsets by default
3. **`@api.one`** — removed; iterate explicitly if needed
4. **`fields.Date.today()` as default** — use `fields.Date.context_today` or `default=fields.Date.today`
5. **`self.pool`** — use `self.env` instead
6. **`cr.execute` for ORM operations** — use ORM methods; raw SQL only for performance-critical bulk ops
7. **`_columns` dict** — use class-level field declarations
8. **`request.website` in non-website modules** — check `has_group` or use `ir.http`
9. **Hardcoded user IDs** — use `self.env.ref('base.user_admin')` or `self.env.user`
10. **Missing `depends` on computed fields** — always declare `@api.depends`; missing deps cause stale cache

### ERRORS.md workflow

When you encounter a new error:
1. Check `ERRORS.md` for an existing solution.
2. If not found, solve it, then add a new `ERR-NNN` entry with symptom, cause, and solution.
3. Commit `ERRORS.md` so the fix is available in future sessions.

## Refreshing AI Context

Run `odoodev context` whenever:
- A new module is added or scaffolded
- Models or fields change significantly
- Starting a new Claude Code session on this project

The generated `PROJECT_CONTEXT.md` (gitignored) gives Claude a compact map of all custom modules,
their models, fields, view counts, and dependencies — without requiring access to every source file.
