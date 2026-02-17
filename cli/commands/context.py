import ast
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from cli.core.config import load_env
from cli.core.console import info, success, warning
from cli.core.paths import ADDONS_DIR, CLI_TEMPLATES_DIR, PROJECT_ROOT


def context() -> None:
    """Generate PROJECT_CONTEXT.md from addons/ module analysis."""
    env = load_env()
    modules = _scan_modules(ADDONS_DIR)

    if not modules:
        warning("No modules found in addons/. PROJECT_CONTEXT.md will be minimal.")

    jinja_env = Environment(
        loader=FileSystemLoader(str(CLI_TEMPLATES_DIR)),
        keep_trailing_newline=True,
    )
    template = jinja_env.get_template("project_context.md.j2")

    output = template.render(
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        odoo_version=env.get("ODOO_VERSION", "N/A"),
        db_name=env.get("DB_NAME", "N/A"),
        modules=modules,
    )

    target = PROJECT_ROOT / "PROJECT_CONTEXT.md"
    target.write_text(output)
    success(f"Generated {target.name} with {len(modules)} module(s).")


def _scan_modules(addons_dir: Path) -> list[dict]:
    """Scan addons directory for Odoo modules using ast (no imports)."""
    if not addons_dir.exists():
        return []

    modules = []
    for manifest_path in sorted(addons_dir.glob("*/__manifest__.py")):
        module_dir = manifest_path.parent
        module_info = _parse_manifest(manifest_path)
        if module_info is None:
            continue

        module_info["technical_name"] = module_dir.name
        module_info["models"] = _scan_models(module_dir / "models")
        module_info["model_count"] = len(module_info["models"])
        module_info["view_count"] = _count_xml_views(module_dir)
        module_info["test_count"] = _count_tests(module_dir)
        module_info["has_controllers"] = _has_controllers(module_dir)
        module_info["report_count"] = _count_xml_reports(module_dir)
        module_info["wizard_count"] = _count_wizards(module_dir)
        modules.append(module_info)

    return modules


def _parse_manifest(path: Path) -> dict | None:
    """Parse __manifest__.py using ast.literal_eval (safe, no execution)."""
    try:
        content = path.read_text()
        manifest = ast.literal_eval(content)
        if not isinstance(manifest, dict):
            return None
        return {
            "name": manifest.get("name", path.parent.name),
            "summary": manifest.get("summary", ""),
            "version": manifest.get("version", ""),
            "depends": manifest.get("depends", []),
        }
    except (ValueError, SyntaxError):
        return None


def _scan_models(models_dir: Path) -> list[dict]:
    """Scan models/*.py files for Odoo model classes using ast.parse."""
    if not models_dir.exists():
        return []

    models = []
    for py_file in sorted(models_dir.glob("*.py")):
        if py_file.name == "__init__.py":
            continue
        try:
            tree = ast.parse(py_file.read_text())
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            model_info = _extract_model_info(node)
            if model_info:
                models.append(model_info)

    return models


def _extract_model_info(class_node: ast.ClassDef) -> dict | None:
    """Extract _name, _inherit, and field definitions from a class node."""
    model_name = None
    inherit = None
    fields = []

    for item in class_node.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name):
                    if target.id == "_name" and isinstance(item.value, ast.Constant):
                        model_name = item.value.value
                    elif target.id == "_inherit" and isinstance(item.value, ast.Constant):
                        inherit = item.value.value

                    # Check if assignment is a field (Call to fields.Xxx)
                    if isinstance(item.value, ast.Call):
                        field_type = _get_field_type(item.value)
                        if field_type:
                            fields.append(f"{target.id} ({field_type})")

    if not model_name and not inherit:
        return None

    return {
        "name": model_name or inherit or class_node.name,
        "inherit": inherit,
        "fields": fields,
    }


def _get_field_type(call_node: ast.Call) -> str | None:
    """Extract field type from a fields.Xxx() call."""
    func = call_node.func
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        if func.value.id == "fields":
            return func.attr
    return None


def _count_xml_views(module_dir: Path) -> int:
    """Count ir.ui.view records in views/*.xml files."""
    count = 0
    views_dir = module_dir / "views"
    if not views_dir.exists():
        return 0
    for xml_file in views_dir.glob("*.xml"):
        try:
            content = xml_file.read_text()
            count += content.count('model="ir.ui.view"')
        except OSError:
            continue
    return count


def _count_xml_reports(module_dir: Path) -> int:
    """Count ir.actions.report records in all *.xml files of the module."""
    count = 0
    for xml_file in module_dir.rglob("*.xml"):
        try:
            content = xml_file.read_text()
            count += content.count('model="ir.actions.report"')
        except OSError:
            continue
    return count


def _count_tests(module_dir: Path) -> int:
    """Count test methods (def test_*) in tests/*.py files."""
    count = 0
    tests_dir = module_dir / "tests"
    if not tests_dir.exists():
        return 0
    for py_file in tests_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        try:
            tree = ast.parse(py_file.read_text())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                count += 1
    return count


def _has_controllers(module_dir: Path) -> bool:
    """Return True if controllers/ has any .py files besides __init__.py."""
    controllers_dir = module_dir / "controllers"
    if not controllers_dir.exists():
        return False
    return any(
        f for f in controllers_dir.glob("*.py") if f.name != "__init__.py"
    )


def _count_wizards(module_dir: Path) -> int:
    """Count TransientModel classes in wizards/ or wizard/ directories."""
    count = 0
    for wizard_dir_name in ("wizards", "wizard"):
        wizard_dir = module_dir / wizard_dir_name
        if not wizard_dir.exists():
            continue
        for py_file in wizard_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            try:
                tree = ast.parse(py_file.read_text())
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for base in node.bases:
                        if isinstance(base, ast.Attribute) and base.attr == "TransientModel":
                            count += 1
                        elif isinstance(base, ast.Name) and base.id == "TransientModel":
                            count += 1
    return count
