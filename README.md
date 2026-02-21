# mnemos

Sistema de gestión de tiempo personal para **un solo usuario**.

mnemos te ayuda a gestionar tu tiempo recolectando ideas, items del inbox, y organizando tu día a día.

## 🚀 Características

- **Ideas**: Captura ideas rápidamente sin preocuparte por organizarlas
- **Inbox**: Recolecta items durante el día desde diferentes fuentes (manual, CLI, web, discord)
- **Statuses & Priorities**: Organiza tus items con estados y prioridades
- **API REST**: Acceso completo via FastAPI

## 📋 Requisitos

- Python 3.11+
- uv (gestor de paquetes)

## 🔧 Instalación

1. Clonar el repositorio:
```bash
git clone <tu-repo>
cd mnemos
```

2. Instalar dependencias con uv:
```bash
uv sync
```

3. Configurar variables de entorno (opcional):
```bash
cp .env.example .env
# Edita .env con tus datos
```

4. Iniciar ambos servicios (API + UI):
```bash
uv run start.py
```

Esto iniciará:
- **FastAPI**: http://localhost:8000 (API REST + Documentación)
- **Streamlit**: http://localhost:8501 (Dashboard interactivo)

> 📖 **Ver [docs/STARTUP.md](docs/STARTUP.md)** para más opciones de inicio y troubleshooting

**Alternativamente**, puedes iniciar cada servicio por separado:

```bash
# Solo la API
uv run start-api

# Solo la UI
uv run start-ui

# O manualmente
uv run uvicorn main:app --reload
uv run streamlit run streamlit_app.py
```

## 📚 Interfaces

Una vez iniciados los servicios, accede a:
- **📊 Dashboard**: http://localhost:8501 (Streamlit UI)
- **📡 API Docs**: http://localhost:8000/docs (Swagger UI)
- **📖 ReDoc**: http://localhost:8000/redoc (Documentación alternativa)

## 🗂️ Estructura del Proyecto

```
mnemos/
├── main.py              # Punto de entrada de la aplicación
├── database.py          # Configuración de base de datos
├── models/              # Modelos SQLAlchemy
│   ├── user.py
│   ├── idea.py
│   ├── inbox_item.py
│   ├── status.py
│   └── priority.py
├── schemas/             # Schemas Pydantic
│   ├── user.py
│   ├── idea.py
│   ├── inbox_item.py
│   ├── status.py
│   └── priority.py
├── routers/             # Endpoints FastAPI
│   ├── user.py
│   ├── idea.py
│   ├── inbox_item.py
│   ├── status.py
│   └── priority.py
├── dependencies/        # Dependencias compartidas
│   ├── database.py      # get_db()
│   └── user.py          # get_current_user_id()
└── utils/               # Utilidades
    ├── seed.py          # Seeds iniciales
    └── logger.py        # Logging
```

## 🔐 Variables de Entorno

Crea un archivo `.env` basado en `.env.example`:

```env
# Base de datos (SQLite por defecto, PostgreSQL para producción)
DB_TYPE=sqlite
SQLITE_PATH=./db.sqlite3

# Usuario por defecto
DEFAULT_USER_ID=1
DEFAULT_USER_NAME=Tu Nombre
DEFAULT_USER_EMAIL=tu@email.com
DEFAULT_USER_BIRTH=1990-01-01

# Google Calendar (opcional)
GOOGLE_SERVICE_ACCOUNT_FILE=credentials/service-account.json
GOOGLE_CALENDAR_ID=tu@email.com
TIMEZONE=America/Lima
```

### Opciones de Base de Datos

**SQLite** (Desarrollo - por defecto):
```env
DB_TYPE=sqlite
SQLITE_PATH=./db.sqlite3
```

**PostgreSQL** (Producción):
```env
DB_TYPE=postgresql
POSTGRES_USER=mnemos_user
POSTGRES_PASSWORD=contraseña
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mnemos_db
```

Ver [docs/DATABASE_SETUP.md](docs/DATABASE_SETUP.md) para instrucciones detalladas.

## 📡 Endpoints Principales

### Ideas
- `POST /api/v1/ideas/` - Crear idea
- `GET /api/v1/ideas/` - Listar ideas
- `GET /api/v1/ideas/{id}` - Obtener idea
- `PUT /api/v1/ideas/{id}` - Actualizar idea
- `DELETE /api/v1/ideas/{id}` - Eliminar idea

### Inbox
- `POST /api/v1/inbox/` - Crear inbox item
- `GET /api/v1/inbox/` - Listar inbox items
- `GET /api/v1/inbox/{id}` - Obtener inbox item
- `PUT /api/v1/inbox/{id}` - Actualizar inbox item
- `DELETE /api/v1/inbox/{id}` - Eliminar inbox item

### Usuarios
- `POST /api/v1/users/` - Crear usuario
- `GET /api/v1/users/` - Listar usuarios

## 🎯 Uso Rápido

Crear una idea:
```bash
curl -X POST http://localhost:8000/api/v1/ideas/ \
  -H "Content-Type: application/json" \
  -d '{"content": "Mi nueva idea", "user_id": null}'
```

Crear inbox item:
```bash
curl -X POST http://localhost:8000/api/v1/inbox/ \
  -H "Content-Type: application/json" \
  -d '{"content": "Item del inbox", "source": "manual", "user_id": null}'
```

## 🔮 Roadmap

- [x] Integración con Google Calendar API
- [x] Soporte para PostgreSQL
- [x] Frontend con Streamlit
- [x] Sistema de colores para categorías de eventos
- [x] Analytics y métricas para Calendar, Ideas e Inbox
- [ ] Containerización con Docker
- [ ] Tests automatizados
- [ ] Integración con Telegram
- [ ] Autenticación JWT

## 🛠️ Tecnologías

- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para Python
- **Pydantic** - Validación de datos
- **SQLite / PostgreSQL** - Base de datos
- **Google Calendar API** - Sincronización de eventos
- **uv** - Gestor de paquetes ultrarrápido

## 📝 Licencia

Este es un proyecto personal.

---

**mnemos** - Gestiona tu tiempo de forma simple y efectiva
