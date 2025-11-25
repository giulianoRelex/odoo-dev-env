# VitalCare Odoo Development Environment

Este repositorio contiene el entorno de desarrollo para el proyecto VitalCare Odoo.
Se ha actualizado para ser totalmente contenerizado y configurable.

## 📋 Requisitos

- Docker
- Docker Compose (v2 recomendado)

## 🚀 Configuración Inicial

1. **Variables de Entorno**:
   Copia el archivo de ejemplo y ajústalo según tus necesidades:
   ```bash
   cp .env.example .env
   ```
   Edita `.env` para configurar puertos, contraseñas, versión de Odoo, etc.

2. **Módulos Enterprise**:
   Asegúrate de colocar los módulos Enterprise en el directorio `enterprise-18.0/` si los necesitas.

## 🛠 Uso del Entorno

Utiliza el script `control.sh` para gestionar el entorno de manera sencilla.

### Menú Interactivo
Ejecuta el script sin argumentos:
```bash
./control.sh
```

### Comandos Rápidos
- **Iniciar**: `./control.sh start`
- **Detener**: `./control.sh stop`
- **Reiniciar Web**: `./control.sh restart`
- **Ver Logs**: `./control.sh logs`
- **Shell Odoo**: `./control.sh shell`
- **Estado**: `./control.sh status`
- **Resetear DB**: `./control.sh reset_db` (¡Cuidado! Borra todo)

## 📂 Estructura del Proyecto

```
.
├── addons/                  # Tus módulos personalizados
├── config/                  # Configuración de Odoo (odoo.conf)
├── enterprise-18.0/         # Módulos Enterprise
├── .env                     # Variables de entorno (NO commitear)
├── control.sh               # Script de gestión
├── docker-compose.yml       # Definición de servicios
└── README.md                # Documentación
```

## 📝 Notas de Desarrollo

- **Addons**: Desarrolla tus módulos en `addons/`. Se montan automáticamente en el contenedor.
- **Cambios en Python**: Requieren reiniciar el servicio web (`./control.sh restart`).
- **Cambios en XML**: Generalmente se aplican al actualizar el módulo (`./control.sh update_module` o desde la UI).

---
**VitalCare Odoo Team**
