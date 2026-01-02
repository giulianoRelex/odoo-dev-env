# Odoo Development Environment

Este repositorio contiene un entorno de desarrollo para proyectos Odoo 18.0.
Se ha actualizado para ser totalmente contenerizado, configurable y orientado a la eficiencia del desarrollador.

## 📋 Requisitos

- Docker
- Docker Compose (v2 recomendado)
- VS Code (recomendado para aprovechar Dev Containers)

## 🚀 Configuración Inicial

1. **Variables de Entorno**:
   Copia el archivo de ejemplo y ajústalo según tus necesidades:

   ```bash
   cp .env.example .env
   ```

   Edita `.env` para configurar puertos, contraseñas, versión de Odoo, etc. Especialmente revisa `PGWEB_PORT` y `DEBUGPY`.

2. **Módulos Enterprise**:
   Asegúrate de colocar los módulos Enterprise en el directorio `enterprise-18.0/` si los necesitas.

## 🛠 Uso del Entorno

Utiliza el script `control.sh` para gestionar el entorno de manera sencilla.

### Comandos Rápidos

- **Iniciar**: `./control.sh start`
- **Detener**: `./control.sh stop`
- **Reiniciar Web**: `./control.sh restart`
- **Ver Logs**: `./control.sh logs`
- **Shell Odoo**: `./control.sh shell`
- **Scaffold**: `./control.sh scaffold <nombre_modulo>` (Crea un nuevo módulo)
- **Test**: `./control.sh test <nombre_modulo>` (Corre los tests del módulo)
- **Estado**: `./control.sh status`
- **Resetear DB**: `./control.sh reset_db` (¡Cuidado! Borra todos los volúmenes y datos)

## 💎 Características Avanzadas

### 🗄️ Gestión de Base de Datos (pgweb)
El entorno incluye `pgweb`, una interfaz web ligera para PostgreSQL.
- **URL**: `localhost:8081` (o el puerto configurado en `PGWEB_PORT`)

### 🐞 Debugging Avanzado (debugpy)
Puedes hacer debug línea a línea de Odoo usando VS Code.
1. Cambia `DEBUGPY=True` en tu archivo `.env`.
2. Reinicia el entorno: `./control.sh restart`.
3. Adjunta el debugger de VS Code al puerto `5678`.

### 📦 VS Code Dev Containers
Este proyecto está configurado para ejecutarse totalmente dentro de un contenedor.
- Al abrir la carpeta en VS Code, selecciona **"Reopen in Container"**.
- Esto instalará automáticamente las extensiones necesarias y configurará el entorno de Python para que el IntelliSense funcione correctamente con el core de Odoo.

### 🔍 Análisis Estático (pre-commit)
Se incluyen hooks de `pre-commit` para asegurar la calidad del código.
- **Herramientas**: `ruff`, `pylint-odoo`, `eslint`.
- Para instalar localmente: `pre-commit install`.

## 📂 Estructura del Proyecto

```text
.
├── addons/                  # Tus módulos personalizados
├── config/                  # Configuración de Odoo (odoo.conf)
├── enterprise-18.0/         # Módulos Enterprise
├── templates/               # Plantillas para nuevos módulos
├── .devcontainer/           # Configuración de VS Code Dev Container
├── .env                     # Variables de entorno (NO commitear)
├── control.sh               # Script de gestión (CLI & Interactivo)
├── docker-compose.yml       # Definición de servicios (web, db, pgweb)
└── README.md                # Documentación
```

## 📝 Notas de Desarrollo

- **Addons**: Desarrolla tus módulos en `addons/`. Se montan automáticamente en el contenedor.
- **Hot Reload**: El entorno tiene habilitado `--dev=reload,xml`, por lo que los cambios en Python reinician el server y los cambios en XML se aplican al refrescar (usualmente).
- **Control**: El menú interactivo de `./control.sh` es la forma más rápida de navegar por las opciones.

---

### Giuliano Hillebrand
