# Plan de Merge: refactor/reswoy-submodules → production

**Fecha**: 2026-03-11
**Repo**: `reswoy/vitalcare-erp`
**Merge base**: `7b6d559`

---

## Estado actual

- **production** (`c8d48d1`): 3 commits ahead del merge base. Tiene forks de reswoy para 3 repos de ingadhoc (resabio de la migracion a v19, olvidaron revertir).
- **refactor/reswoy-submodules** (`d5486d6`): 7 commits ahead del merge base. Reorganiza submodules de reswoy como repos independientes, corrige URLs de forks a upstream.

---

## Conflictos esperados

### 1. `.gitmodules` (conflicto de texto — 3 bloques)

Tres submodules que production apunta a forks `reswoy/*` y refactor ya corrigio a upstream `ingadhoc/*`:

| Repo | Production (fork) | Refactor (upstream) | Accion |
|---|---|---|---|
| `odoo-argentina` | `reswoy/odoo-argentina.git` en path `reswoy/odoo-argentina` | `ingadhoc/odoo-argentina.git` en path `ingadhoc/odoo-argentina` | Aceptar refactor (upstream + nuevo path) |
| `odoo-argentina-ee` | URL `reswoy/odoo-argentina-ee.git` | URL `ingadhoc/odoo-argentina-ee.git` | Aceptar refactor (upstream URL) |
| `sale` | URL `reswoy/sale.git` | URL `ingadhoc/sale.git` | Aceptar refactor (upstream URL) |

**Motivo**: Los forks se usaron para aplicar migration scripts durante la migracion a v19 y debieron revertirse a upstream una vez completada.

### 2. `reswoy/odoo-argentina` — delete vs add

Production tiene el submodule en `reswoy/odoo-argentina`. Refactor lo movio a `ingadhoc/odoo-argentina`. El merge vera un conflicto delete/modify.

**Resolucion**: Eliminar `reswoy/odoo-argentina` y mantener `ingadhoc/odoo-argentina` (version refactor).

### 3. Submodule pointer conflicts (3 repos)

Ambas ramas avanzaron estos submodules a commits diferentes desde el merge base:

| Path | Production | Refactor | Accion |
|---|---|---|---|
| `OCA/sale-workflow` | `269d04b` | `87113dc` | Usar el mas reciente |
| `ingadhoc/odoo-argentina-ee` | `1c4e647` | `405d215` | Usar refactor (upstream) |
| `ingadhoc/sale` | `e0c3784` | `f270438` | Usar refactor (upstream) |

---

## Lo que mergea limpio (sin conflictos)

- 3 submodules nuevos: `reswoy/maximia-hr`, `reswoy/ntgs_base`, `reswoy/reswoy_healthcare`
- `payment_pay_way/__manifest__.py` version bump 18.0 → 19.0
- Todos los demas submodules de ingadhoc (commits identicos en ambas ramas)
- `CLAUDE.md`, `README.md` (sin cambios)

---

## Procedimiento de merge

```bash
# 1. Desde la rama refactor (ya checkeada)
cd vitalcare-erp
git checkout refactor/reswoy-submodules
git fetch origin production

# 2. Merge production INTO refactor (resolver conflictos en refactor, no en production)
git merge origin/production

# 3. Resolver .gitmodules — aceptar la version de refactor (ours)
git checkout --ours .gitmodules
git add .gitmodules

# 4. Resolver odoo-argentina path conflict
git rm reswoy/odoo-argentina   # eliminar el path viejo de production
git add ingadhoc/odoo-argentina  # mantener el de refactor

# 5. Resolver submodule pointer conflicts — usar los commits de refactor
git checkout --ours OCA/sale-workflow
git checkout --ours ingadhoc/odoo-argentina-ee
git checkout --ours ingadhoc/sale
git add OCA/sale-workflow ingadhoc/odoo-argentina-ee ingadhoc/sale

# 6. Completar merge
git commit

# 7. Sync submodules
git submodule sync --recursive
git submodule update --init --recursive

# 8. Verificar
git submodule status  # todos deben mostrar commits sin prefijo +/-

# 9. Push refactor y crear PR hacia production
git push origin refactor/reswoy-submodules
# Luego hacer PR refactor/reswoy-submodules → production en GitHub
```

---

## Verificacion post-merge

1. Todos los submodules apuntan a `ingadhoc/*` (upstream), no a `reswoy/*` (forks)
2. Los 3 submodules nuevos de reswoy estan presentes con paths con underscore
3. `payment_pay_way` tiene version `19.0.1.0.0`
4. No quedan referencias a `git@relex:` en `.gitmodules`
5. No queda el directorio `reswoy/odoo-argentina` (movido a `ingadhoc/`)
6. Build en Odoo.sh pasa verde

---

## Notas adicionales

- La rama `production` en Odoo.sh es 19.0. Los submodules deben apuntar a ramas 19.0.
- `card_installment` esta en `ingadhoc/account-payment` y ya tiene version 19.0 — no requiere cambios.
- Los deploy keys de Odoo.sh ya estan configurados en los 3 repos privados de reswoy en GitHub.
