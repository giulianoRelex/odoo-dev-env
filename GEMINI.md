# Project Context: Odoo 18.0 Development Environment

## Overview
This repository hosts a fully containerized development environment for Odoo 18.0 projects. It is designed to facilitate the development of custom Odoo addons and the integration of Odoo Enterprise modules. The infrastructure is managed via Docker Compose.

## Architecture
The system consists of two primary services defined in `docker-compose.yml`:
- **`web`**: The Odoo application server.
- **`db`**: A PostgreSQL database server.

### Key Directories
- **`addons/`**: Location for custom Odoo modules. Mapped to `/mnt/extra-addons`.
- **`enterprise-18.0/`**: Location for Odoo Enterprise source code. Mapped to `/mnt/enterprise-addons`.
- **`config/`**: Contains `odoo.conf` for Odoo server configuration.
- **`logs/`**: Persisted logs for both Odoo and Postgres.
- **`control.sh`**: A helper script to manage the Docker environment.

## Operational Commands
The project includes a `control.sh` script to abstract Docker Compose commands.

- **Start Services**: `./control.sh start`
- **Stop Services**: `./control.sh stop`
- **Restart Web Service**: `./control.sh restart` (Required for Python code changes)
- **View Logs**: `./control.sh logs`
- **Open Odoo Shell**: `./control.sh shell`
- **Check Status**: `./control.sh status`
- **Reset Database**: `./control.sh reset_db` (WARNING: Destructive action)
- **Update Module**: `./control.sh update_module <module_name>` (Applies XML/View changes)

## Configuration
- **Environment Variables**: Managed in `.env` (template provided in `.env.example`).
- **Odoo Config**: Managed in `config/odoo.conf`.

## Development Workflow
1.  **Custom Modules**: Create new modules within the `addons/` directory.
2.  **Code Updates**:
    - **Python**: Requires a restart of the web service (`./control.sh restart`).
    - **XML/Assets**: Requires a module upgrade (`./control.sh update_module` or via UI).
3.  **Database Access**: Credentials are defined in `.env`.

## AI Assistant Guidelines
- **Documentation**: Always use the `context7` MCP service to search for the Odoo 18 documentation library. This ensures adherence to the latest Odoo 18 best practices, API changes, and development guidelines.
