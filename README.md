# Odoo Dev Environment

A generic, reusable boilerplate for Odoo development with Docker. Clone it, run the setup wizard, and start building modules.

**Default stack:** Odoo 19 + PostgreSQL 16 (with pgvector) + pgweb

## Requirements

- Docker with Compose v2
- Python 3.10+
- VS Code (optional, for Dev Container support)

## Quick Start

```bash
git clone <this-repo> my-project
cd my-project
pip install -e .
odoodev init          # Interactive setup wizard (Odoo 19 by default)
odoodev up            # Start Odoo + PostgreSQL + pgweb
```

Open `http://localhost:8069` in your browser.

## Services

| Service | URL | Description |
|---|---|---|
| Odoo web | `http://localhost:8069` | Odoo application (dev mode with hot-reload) |
| pgweb | `http://localhost:8081` | Database browser UI |
| debugpy | `localhost:5678` | VS Code remote debugger (when `DEBUGPY=True`) |

## CLI Reference

```bash
# Environment
odoodev up [--build] [--watch]   # Start services
odoodev down                     # Stop services
odoodev restart                  # Restart Odoo web container
odoodev status                   # Service status table
odoodev reset-db                 # Destroy DB + volumes, fresh start

# Development
odoodev shell                    # Bash shell in Odoo container
odoodev scaffold <name>          # Create module from template
odoodev addon-install <module>   # Install module for the first time
odoodev update <module>          # Upgrade module + restart
odoodev logs [web|db|all]        # Follow service logs

# Testing
odoodev test <module>            # Run module tests
odoodev test all                 # Run all tests

# Database
odoodev db snapshot <name>       # Save database dump
odoodev db restore <name>        # Restore from dump
odoodev db list                  # List snapshots
odoodev db anonymize             # Anonymize personal data
odoodev load-backup <path>       # Load Odoo.sh / DB Manager backup

# Tools
odoodev context                  # Generate PROJECT_CONTEXT.md
odoodev tui                      # Launch TUI dashboard
```

## TUI Dashboard

`odoodev tui` launches an interactive terminal dashboard with:

- **Status panel**: Live service status (auto-refreshes every 3s)
- **Log viewer**: Streaming Odoo logs
- **Quick actions**: Keyboard shortcuts for common operations

## Database Operations

### Snapshots

Save and restore database state at any point:

```bash
odoodev db snapshot clean_install    # Save current DB
# ... make changes, break things ...
odoodev db restore clean_install     # Restore to saved state
odoodev db list                      # See all snapshots
```

### Load External Backups

Import an Odoo.sh or Database Manager backup (`.zip` with `dump.sql` + optional `filestore/`):

```bash
odoodev load-backup /path/to/backup.zip
```

Automatically drops the current DB, restores the dump, copies the filestore, and neutralizes the database (disables crons, mail servers, etc.). Use `--no-neutralize` to skip neutralization.

### Anonymization

Strip personal data from a production database copy for development:

```bash
odoodev db anonymize
```

Replaces names, emails, and phones with fake data. Resets all user passwords to `admin`.

## Module Development

```bash
odoodev scaffold my_module     # Creates addons/my_module/ with:
                               #   - __manifest__.py (v19.0)
                               #   - models/ (example model with fields)
                               #   - views/ (list + form + action + menu)
                               #   - security/ (ACL)
                               #   - tests/ (example TransactionCase)
```

After editing Python models or data files:

```bash
odoodev addon-install my_module   # First time: install the module
odoodev update my_module          # After changes: applies and restarts
```

XML and JS changes are picked up automatically (dev mode hot-reload).

## Odoo 19 Reference Guides

The `skills/odoo-19.0/` directory contains 18 specialized development guides covering all aspects of Odoo 19:

| Guide | Covers |
|---|---|
| Actions | ir.actions.*, cron jobs, server actions, menus |
| Controllers | HTTP routing, endpoints, authentication |
| Data Files | XML/CSV records, shortcuts, noupdate |
| Decorators | @api.depends, @api.constrains, @api.ondelete, @api.private |
| Development | Module creation, manifest, wizards, reports |
| Fields | All field types, parameters, relations |
| Manifest | `__manifest__.py` configuration |
| Migration | Pre/post/end hooks, data migration scripts |
| Mixins | mail.thread, mail.activity, mail.alias, utm |
| Models | ORM, CRUD, search, domain filters, recordsets |
| OWL | Frontend components, hooks, services, lifecycle |
| Performance | N+1 prevention, batch operations, _read_group |
| Reports | QWeb PDF/HTML, paper formats, barcodes |
| Security | ACL, record rules, field permissions, @api.private |
| Testing | TransactionCase, HttpCase, mocking, assertions |
| Transactions | Savepoints, UniqueViolation, serialization |
| Translation | i18n, PO files, translatable fields |
| Views | list/form/search, kanban, xpath inheritance, QWeb |

These guides are useful both for human developers and as context for AI coding assistants.

## Linting

Pre-commit hooks run automatically on `git commit`:

- **ruff**: Python linting + formatting
- **pylint-odoo**: Odoo-specific rules
- **eslint**: JavaScript and XML (with OWL plugin)

Install hooks:

```bash
pip install pre-commit
pre-commit install
```

Config locations:
- Python: `pyproject.toml` (`[tool.ruff]`, `[tool.pylint]`)
- JavaScript: `.eslintrc.json`
- Hooks: `.pre-commit-config.yaml`

## AI Agent Integration

### MCP Servers

Five MCP servers are pre-configured in `.mcp.json.example` for Claude Code and compatible AI agents:

| Server | Capability |
|---|---|
| `postgres` | Query the live Odoo DB directly |
| `filesystem` | Read/write project files |
| `fetch` | Fetch Odoo docs and web pages |
| `context7` | Up-to-date library documentation |
| `memory` | Persistent cross-session memory |

```bash
cp .mcp.json.example .mcp.json
# Edit: replace DB credentials and absolute paths
# Restart Claude Code, then run /mcp to verify
```

### Project Context Generation

Generate a machine-readable project context from your custom modules:

```bash
odoodev context
```

Creates `PROJECT_CONTEXT.md` with module list, model definitions, fields, and dependency graph. Useful as context input for AI coding assistants.

## Debugging

Enable `debugpy` for VS Code remote debugging:

1. Set `DEBUGPY=True` in `.env`
2. `odoodev restart`
3. Attach VS Code debugger to port 5678

## Project Structure

```
cli/                        # Python CLI (odoodev)
config/                     # Runtime odoo.conf (auto-generated)
addons/                     # Your custom modules (gitignored)
enterprise/                 # Enterprise modules (gitignored, optional)
snapshots/                  # Database snapshots (gitignored)
skills/odoo-19.0/           # Odoo 19 development reference guides
templates/module_template/  # Scaffold template
docker-compose.yml          # Docker services
entrypoint.sh               # Container entrypoint
pyproject.toml              # CLI package + tool config
.env.example                # Environment template
.mcp.json.example           # MCP server config template
```

## Configuration

The setup wizard (`odoodev init`) configures everything interactively. You can also copy and edit `.env.example` manually:

| Variable | Default | Purpose |
|---|---|---|
| `ODOO_VERSION` | `19.0` | Odoo version |
| `ODOO_IMAGE` | `odoo:19` | Docker image for Odoo |
| `DB_IMAGE` | `pgvector/pgvector:pg16` | PostgreSQL with pgvector |
| `WEB_PORT` | `8069` | Odoo web port |
| `PGWEB_PORT` | `8081` | pgweb port |
| `LOAD_LANGUAGE` | `en_US` | Language to auto-install |
| `WITHOUT_DEMO` | `all` | Skip demo data |
| `DEBUGPY` | `False` | Enable remote debugger |

## Dev Container

Open the project in VS Code and select **"Reopen in Container"**. Extensions for Python, Odoo, and linting are auto-installed.
