# ERRORS.md

Known errors, solutions, and workarounds for this Odoo 18 project.
Add new entries as you encounter and solve issues.

---

## ERR-001: Module not visible after scaffold

**Symptom**: After running `odoodev scaffold my_module`, the module does not appear in the Apps
menu even after enabling developer mode.

**Cause**: Odoo's module list cache is stale, or the module directory was not picked up on startup.

**Solution**:
```bash
# Update the module list from Settings > Apps > Update Apps List
# Or force a full restart with update:
odoodev update my_module
```

If the module still doesn't appear, check that `__manifest__.py` has `'installable': True` and
that the `addons/` directory is correctly mounted (`/mnt/extra-addons`).

---

## ERR-002: UndefinedColumn when updating after renaming a field

**Symptom**: `ProgrammingError: column my_model.old_field_name does not exist` after renaming a
field in Python and running `odoodev update my_module`.

**Cause**: Odoo does not automatically rename database columns. The old column still exists and
the new one hasn't been created yet, or vice versa.

**Solution**:
```python
# Option A: Use _sql_constraints or a migration script
# Option B: Add a pre-migration script in my_module/migrations/<version>/pre-migrate.py:
def migrate(cr, version):
    cr.execute("ALTER TABLE my_model RENAME COLUMN old_field_name TO new_field_name")
```

Or drop the DB and start fresh during development: `odoodev reset-db`.

---

## ERR-003: TransactionRollbackError in tests (concurrent update)

**Symptom**: `TransactionRollbackError: could not serialize access due to concurrent update`
during `odoodev test my_module`.

**Cause**: Two transactions attempted to update the same record simultaneously (common in tests
that use `threading` or `@job` decorators without proper isolation).

**Solution**: Ensure each test method uses `self.env.cr.savepoint()` or isolates writes. Avoid
sharing record IDs between test methods that run concurrently.

```python
def test_something(self):
    with self.env.cr.savepoint():
        record = self.env['my.model'].create({...})
        # assertions...
```

---

## ERR-004: View arch validation error (ir.ui.view)

**Symptom**: `ValidationError: Invalid arch content (parsing only)` when updating a module with
custom views.

**Cause**: XML syntax error or invalid Odoo view element in `views/*.xml`.

**Solution**:
1. Check the view XML against the Odoo 18 view schema.
2. Common culprits: missing `string` attribute on `<field>`, unclosed tags, invalid `widget`
   names.
3. Use `odoodev logs web` to see the full traceback pointing to the problematic view file.

---

## ERR-005: `attrs` / `states` attributes removed in Odoo 18

**Symptom**: Views silently ignore `attrs` or `states` attributes, or raise a warning like
`attrs is not supported anymore`.

**Cause**: Odoo 18 replaced `attrs` and `states` with `invisible`, `readonly`, and `required`
domain attributes directly on field elements.

**Solution**:
```xml
<!-- OLD (Odoo 16/17) -->
<field name="my_field" attrs="{'invisible': [('state', '=', 'done')]}"/>

<!-- NEW (Odoo 18) -->
<field name="my_field" invisible="state == 'done'"/>
```

---

## ERR-006: `onchange` not triggering on client side

**Symptom**: An `@api.onchange` method is defined in Python but the UI does not react when the
field value changes.

**Cause**: In Odoo 18 OWL-based views, `onchange` works differently for some field types. Also,
the field must be present in the form view for the onchange to be triggered.

**Solution**:
1. Ensure the field that triggers the onchange is in the form view (can be `invisible="1"` if
   needed).
2. For computed fields, prefer `@api.depends` with `store=False` over `@api.onchange`.
3. Check browser console for JS errors that may be swallowing the onchange call.

---

## ERR-007: debugpy not connecting

**Symptom**: VS Code debugger cannot attach to the container even though `DEBUGPY=True` is set
in `.env`.

**Cause**: Container not restarted after changing `.env`, or port mapping conflict.

**Solution**:
```bash
# 1. Verify DEBUGPY=True in .env
# 2. Restart the container to apply env changes
odoodev restart

# 3. Check that the port is exposed
odoodev status  # Look for debugpy port in the output

# 4. In entrypoint.sh, debugpy listens on 0.0.0.0:${DEBUGPY_PORT}
# Make sure VS Code launch.json uses the correct port (default 5678)
```

If the port is already in use on the host: change `DEBUGPY_PORT` in `.env` and update
`.vscode/launch.json` accordingly.

---

## ERR-008: PostgreSQL connection fails in tests

**Symptom**: Tests fail with `OperationalError: could not connect to server` or
`FATAL: role "odoo" does not exist`.

**Cause**: Tests are run with `odoodev test`, which executes inside the `web` container. The
`DB_HOST` must point to the `db` service name, not `localhost`.

**Solution**:
Check `config/odoo.conf` (generated from `.env`):
```ini
db_host = db        # Must be the Docker service name, not localhost
db_user = odoo
db_password = odoo
db_name = odoo_db
```

If running tests outside Docker (unusual), set `DB_HOST=localhost` and ensure PostgreSQL is
reachable on `DB_PORT`.

---

## ERR-009: `'res.company' object has no attribute 'tz'` in Odoo 19

**Symptom**: `AttributeError: 'res.company' object has no attribute 'tz'` when calling
`request.env.company.sudo().tz`.

**Cause**: In Odoo 19, the `tz` (timezone) field is on `res.partner`, not `res.company`.
The company's timezone is accessed through its linked partner record.

**Solution**:
```python
# OLD (broken in Odoo 19)
company_tz = request.env.company.sudo().tz or "UTC"

# NEW (correct in Odoo 19)
company_tz = request.env.company.sudo().partner_id.tz or "UTC"
```
