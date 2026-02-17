import re
import shutil

import typer

from cli.core.console import error, info, success
from cli.core.paths import ADDONS_DIR, TEMPLATES_DIR


def scaffold(
    name: str = typer.Argument(..., help="Name of the new module (snake_case)."),
) -> None:
    """Create a new Odoo module from the template."""
    # Validate module name
    if not re.match(r"^[a-z][a-z0-9_]*$", name):
        error("Module name must be snake_case (lowercase letters, digits, underscores, starting with a letter).")
        raise typer.Exit(1)

    template_dir = TEMPLATES_DIR / "module_template"
    if not template_dir.exists():
        error(f"Template directory not found: {template_dir}")
        raise typer.Exit(1)

    target_dir = ADDONS_DIR / name
    if target_dir.exists():
        error(f"Module directory already exists: {target_dir}")
        raise typer.Exit(1)

    ADDONS_DIR.mkdir(parents=True, exist_ok=True)
    info(f"Scaffolding module: {name}")

    # Copy template to target
    shutil.copytree(template_dir, target_dir)

    # Replace __module_name__ in filenames and content
    _replace_in_tree(target_dir, "__module_name__", name)

    success(f"Module created: {target_dir}")
    info("Next steps:")
    info(f"  1. Edit addons/{name}/__manifest__.py")
    info(f"  2. Restart Odoo or run: odoodev update {name}")


def _replace_in_tree(root, placeholder: str, replacement: str) -> None:
    """Replace placeholder in all filenames and file contents under root."""
    # First pass: replace content in files
    for path in sorted(root.rglob("*")):
        if path.is_file():
            try:
                content = path.read_text()
                if placeholder in content:
                    path.write_text(content.replace(placeholder, replacement))
            except UnicodeDecodeError:
                continue

    # Second pass: rename files and directories (deepest first)
    for path in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if placeholder in path.name:
            new_name = path.name.replace(placeholder, replacement)
            path.rename(path.parent / new_name)
