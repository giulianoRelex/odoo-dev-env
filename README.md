# Odoo Dev Environment

A generic, reusable boilerplate for Odoo development with Docker. Clone it, run the setup wizard, and start building modules.

## Requirements

- Docker with Compose v2
- Python 3.10+
- VS Code (optional, for Dev Container support)

## Quick Start

```bash
git clone <this-repo> my-project
cd my-project
pip install -e .
odoodev init          # Interactive setup wizard
odoodev up            # Start Odoo + PostgreSQL + pgweb
```

Open `http://localhost:8069` in your browser.

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

### Anonymization

Strip personal data from a production database copy for development:

```bash
odoodev db anonymize
```

Replaces names, emails, and phones with fake data. Resets all user passwords to `admin`.

## Module Development

```bash
odoodev scaffold my_module     # Creates addons/my_module/ with:
                               #   - __manifest__.py
                               #   - models/ (example model with fields)
                               #   - views/ (tree + form + action + menu)
                               #   - security/ (ACL)
                               #   - tests/ (example TransactionCase)
```

After editing Python models or data files:

```bash
odoodev update my_module       # Applies changes and restarts
```

XML and JS changes are picked up automatically (dev mode hot-reload).

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

Generate a machine-readable project context from your custom modules:

```bash
odoodev context
```

This creates `PROJECT_CONTEXT.md` with:
- Module list with summaries and dependencies
- Model definitions with fields
- Dependency graph

Useful as context input for AI coding assistants.

## Debugging

Enable `debugpy` for VS Code remote debugging:

1. Set `DEBUGPY=True` in `.env`
2. `odoodev restart`
3. Attach VS Code debugger to port 5678

## Project Structure

```
cli/                        # Python CLI (odoodev)
config/                     # Runtime odoo.conf (generated)
addons/                     # Your custom modules
enterprise/                 # Enterprise modules (optional)
snapshots/                  # Database snapshots
templates/module_template/  # Scaffold template
docker-compose.yml          # Docker services
entrypoint.sh               # Container entrypoint
pyproject.toml              # CLI package + tool config
.env.example                # Environment template
```

## Dev Container

Open the project in VS Code and select **"Reopen in Container"**. Extensions for Python, Odoo, and linting are auto-installed.
