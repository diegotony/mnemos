# Mnemos - Documentación Técnica (MVP v1.0)

> **Propósito:** Sistema de gestión personal de tiempo para un único usuario.  
> **Stack:** FastAPI + SQLAlchemy + Google Calendar API  
> **Estado:** MVP funcional - Primera versión robusta  

---

## 📋 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Modelos de Datos](#modelos-de-datos)
5. [API Endpoints](#api-endpoints)
6. [Servicios Externos](#servicios-externos)
7. [Configuración y Deployment](#configuración-y-deployment)
8. [Decisiones de Diseño](#decisiones-de-diseño)
9. [Próximos Pasos](#próximos-pasos)

---

## Visión General

### Propósito
**Mnemos** es una API REST para gestionar tiempo personal de un solo usuario. Permite:
- Capturar ideas rápidamente (inbox)
- Gestionar eventos de calendario (sincronizados con Google Calendar)
- Organizar tareas e ideas por prioridades y estados
- Integrarse con servicios externos (Google Calendar, Telegram a futuro)

### Principios de Diseño
1. **Single-user application**: Todos los foreign keys `user_id` son opcionales/nullable
2. **Simplicidad sobre complejidad**: Código limpio, mantenible y directo
3. **Seguridad por defecto**: Validación exhaustiva, manejo robusto de errores
4. **Configuración declarativa**: Variables de entorno con validación automática
5. **Sin spam**: Integraciones orgánicas y simples (especialmente Telegram)

### Stack Tecnológico
```
Backend:        FastAPI 0.116+
ORM:            SQLAlchemy 2.0+
DB:             SQLite (dev) / PostgreSQL (prod)
Auth:           Google Service Account (para Calendar API)
Package Mgr:    uv
Python:         3.11+
```

---

## Arquitectura del Sistema

### Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                      MNEMOS API (FastAPI)                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Routers    │  │   Services   │  │    Models    │    │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤    │
│  │ • user       │  │ • google     │  │ • User       │    │
│  │ • inbox      │  │   _calendar  │  │ • InboxItem  │    │
│  │ • idea       │──▶│              │  │ • Idea       │    │
│  │ • calendar   │  │              │  │ • Calendar   │    │
│  │ • status     │  │              │  │   Event      │    │
│  │ • priority   │  │              │  │ • Status     │    │
│  └──────────────┘  └──────────────┘  │ • Priority   │    │
│                                       └──────────────┘    │
│                           │                               │
│                           ▼                               │
│                  ┌──────────────────┐                     │
│                  │   Database Layer │                     │
│                  │   (SQLAlchemy)   │                     │
│                  └──────────────────┘                     │
│                           │                               │
└───────────────────────────┼───────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
    ┌──────────────────┐      ┌──────────────────┐
    │  SQLite / Postgres│      │  Google Calendar │
    │   (DB_TYPE env)   │      │   (Service Acct) │
    └──────────────────┘      └──────────────────┘
```

### Flujo de Datos - Sincronización de Calendario

```
┌──────────────┐
│ User Request │  GET /api/v1/calendar/sync/today
└──────┬───────┘
       │
       ▼
┌─────────────────┐
│ Calendar Router │  Valida configuración de Google Calendar
└──────┬──────────┘
       │
       ▼
┌──────────────────────┐
│ GoogleCalendarService│  Llama a Google Calendar API
└──────┬───────────────┘
       │
       ▼
┌──────────────────┐
│ Google Calendar  │  Devuelve eventos en formato Google
│      API         │
└──────┬───────────┘
       │
       ▼
┌──────────────────────┐
│ parse_event()        │  Convierte a formato interno
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Database (SQLAlchemy)│  Upsert eventos
└──────┬───────────────┘  (crea nuevos, actualiza existentes)
       │
       ▼
┌──────────────────┐
│ Response JSON    │  Devuelve lista de eventos
└──────────────────┘
```

---

## Estructura del Proyecto

```
mnemos/
├── main.py                    # Punto de entrada FastAPI
├── database.py                # Configuración SQLAlchemy + validación
├── pyproject.toml             # Dependencias (uv)
├── .env                       # Variables de entorno (local)
├── .env.example               # Template de configuración
│
├── models/                    # Modelos SQLAlchemy (ORM)
│   ├── user.py
│   ├── inbox_item.py
│   ├── idea.py
│   ├── calendar_event.py      ⭐ Principal
│   ├── status.py
│   └── priority.py
│
├── schemas/                   # Pydantic schemas (validación)
│   ├── user.py
│   ├── inbox_item.py
│   ├── idea.py
│   ├── calendar_event.py      ⭐ Principal
│   ├── status.py
│   └── priority.py
│
├── routers/                   # Endpoints API
│   ├── user.py
│   ├── inbox_item.py
│   ├── idea.py
│   ├── calendar.py            ⭐ Principal (CRUD + Sync)
│   ├── status.py
│   └── priority.py
│
├── services/                  # Lógica de negocio
│   └── google_calendar.py     ⭐ Integración con Google
│
├── dependencies/              # Helpers FastAPI
│   └── database.py            # get_db() dependency
│
├── utils/                     # Utilidades
│   ├── logger.py              # Logger con Rich
│   └── seed.py                # Seed data inicial
│
├── credentials/               # Credenciales (gitignored)
│   └── service-account.json   # Google Service Account
│
├── docs/                      # Documentación
│   ├── TECHNICAL_DOCUMENTATION.md    ⭐ Este archivo
│   ├── DATABASE_SETUP.md
│   ├── GOOGLE_CALENDAR_INTEGRATION.md
│   ├── CALENDAR_API_USAGE.md
│   ├── CALENDAR_FIELDS_REFERENCE.md
│   └── CALENDAR_SETUP.md
│
├── tests/                     # Tests (TODO)
└── logs/                      # Logs de la aplicación
```

---

## Modelos de Datos

### Diagrama Entidad-Relación

```
┌─────────────┐
│    User     │
├─────────────┤
│ id (PK)     │
│ name        │
│ email       │
│ created_at  │
└──────┬──────┘
       │
       │ (1 to many, nullable)
       │
   ┌───┴───┬───────────┬────────────┐
   │       │           │            │
   ▼       ▼           ▼            ▼
┌────────┐ ┌────┐ ┌─────────┐ ┌──────────────┐
│Inbox   │ │Idea│ │Calendar │ │   Status     │
│Item    │ │    │ │Event    │ │  Priority    │
└────────┘ └────┘ └─────────┘ └──────────────┘
```

### 1. User (Usuario)

**Propósito:** Representa al usuario único del sistema (single-user app).

```python
class User(Base):
    __tablename__ = "users"
    
    id: int (PK)
    name: str
    email: EmailStr (unique)
    created_at: DateTime (auto)
```

**Campos:**
- `id`: Identificador único
- `name`: Nombre del usuario
- `email`: Email único (validado con Pydantic)
- `created_at`: Timestamp de creación

**Notas de diseño:**
- En modo single-user, se usa `DEFAULT_USER_ID` desde `.env`
- Los foreign keys son **nullable** para permitir uso sin usuario explícito

---

### 2. InboxItem (Elemento de Inbox)

**Propósito:** Captura rápida de ideas, tareas o notas durante el día.

```python
class InboxItem(Base):
    __tablename__ = "inbox"
    
    id: int (PK)
    user_id: int (FK, nullable)
    content: str
    created_at: DateTime (auto)
    status_id: int (FK, nullable)
    source: Enum (manual, cli, web, discord)
```

**Campos:**
- `content`: Texto libre de la captura
- `source`: De dónde vino (manual, CLI, web, Discord)
- `status_id`: Estado actual (pending, processed, etc.)

**Fuentes soportadas:**
- `manual`: Creado directamente en la app
- `cli`: Desde línea de comandos
- `web`: Desde interfaz web (futuro)
- `discord`: Desde bot de Discord (futuro)

---

### 3. Idea

**Propósito:** Ideas archivadas o procesadas desde el inbox.

```python
class Idea(Base):
    __tablename__ = "ideas"
    
    id: int (PK)
    user_id: int (FK, nullable)
    content: str
    created_at: DateTime (auto)
```

**Notas:**
- Almacén permanente de ideas procesadas
- Se puede migrar desde InboxItem cuando se procesa

---

### 4. CalendarEvent ⭐ PRINCIPAL

**Propósito:** Eventos del calendario, sincronizados con Google Calendar o creados localmente.

```python
class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    
    # Identificadores
    id: int (PK)
    google_event_id: str (unique, indexed)
    user_id: int (FK, nullable)
    
    # Contenido del evento
    summary: str                    # Título
    description: str
    location: str (nullable)
    
    # Fechas
    start_datetime: DateTime
    end_datetime: DateTime
    all_day: bool (default=False)
    
    # Estado y organización
    status: str (nullable)          # confirmed, tentative, cancelled
    priority: str (nullable)        # low, medium, high, critical
    category: str (nullable)        # TRABAJO, SALUD, OCIO, RUTINA
    
    # Metadata
    extra_data: JSON (default={})
    created_at: DateTime (auto)
    updated_at: DateTime (auto, onupdate)
    synced_at: DateTime (nullable)  # Última sincronización
```

**Campos clave:**
- `google_event_id`: ID único del evento (de Google o generado localmente)
- `summary`: Título del evento (requerido)
- `start_datetime` / `end_datetime`: Rango temporal (validado: end > start)
- `category`: Categorización custom (TRABAJO, SALUD, OCIO, RUTINA)
- `priority`: Prioridad asignada (low, medium, high, critical)
- `extra_data`: JSON para metadata adicional flexible

**Validaciones:**
- `end_datetime` debe ser posterior a `start_datetime`
- `google_event_id` debe ser único
- Todos los campos de fecha en timezone-aware

**Nota importante:**
- `metadata` es palabra reservada en SQLAlchemy → renombrado a `extra_data`

---

### 5. Status y Priority

**Catálogos de referencia** para estados y prioridades.

```python
class Status(Base):
    __tablename__ = "statuses"
    id: int (PK)
    name: str (unique)

class Priority(Base):
    __tablename__ = "priorities"
    id: int (PK)
    name: str (unique)
```

**Valores iniciales (seeded):**
- Status: `pending`, `in_progress`, `completed`, `archived`
- Priority: `low`, `medium`, `high`, `critical`

---

## API Endpoints

### Prefijo Base
Todos los endpoints están bajo: `/api/v1/`

### 1. Health & Status

```http
GET /
Response: {"message": "Hello World"}
```

---

### 2. Calendar Endpoints ⭐ PRINCIPAL

#### 🔄 Sincronización desde Google Calendar

```http
POST /api/v1/calendar/sync/today
Response: CalendarEventSummary[]
Descripción: Sincroniza eventos del día actual
```

```http
POST /api/v1/calendar/sync/week
Response: CalendarEventSummary[]
Descripción: Sincroniza eventos de la semana actual
```

```http
POST /api/v1/calendar/sync/month
Response: CalendarEventSummary[]
Descripción: Sincroniza eventos del mes actual
```

```http
POST /api/v1/calendar/sync/critical?days_ahead=7
Query Params:
  - days_ahead: int (1-30, default=7)
Response: CalendarEventSummary[]
Descripción: Sincroniza eventos críticos (próximos N días)
```

**Comportamiento:**
- Si el evento ya existe en BD (por `google_event_id`): **actualiza**
- Si no existe: **crea nuevo**
- Actualiza automáticamente `synced_at`
- Devuelve HTTP 503 si Google Calendar no está configurado

---

#### 📋 Consulta de Eventos

```http
GET /api/v1/calendar/events
Query Params:
  - skip: int (default=0)
  - limit: int (default=100)
  - category: str (TRABAJO, SALUD, OCIO, RUTINA)
  - priority: str (low, medium, high, critical)
  - search: str (busca en summary y description, case-insensitive) ⭐ NUEVO
  - start_date: datetime (ISO 8601, filtra por inicio >= fecha) ⭐ NUEVO
  - end_date: datetime (ISO 8601, filtra por fin <= fecha) ⭐ NUEVO

Response: CalendarEventRead[]
Descripción: Lista eventos con filtros opcionales
```

**Ejemplos:**
```bash
# Buscar eventos con "gym"
GET /api/v1/calendar/events?search=gym

# Eventos de esta semana
GET /api/v1/calendar/events?start_date=2026-02-20T00:00:00&end_date=2026-02-27T23:59:59

# Eventos de SALUD con alta prioridad que contengan "gym"
GET /api/v1/calendar/events?category=SALUD&priority=high&search=gym
```

---

```http
GET /api/v1/calendar/events/{id}
Response: CalendarEventRead
Descripción: Obtiene un evento específico
Errors: 404 Not Found
```

---

#### ✏️ Gestión de Eventos (CRUD)

```http
POST /api/v1/calendar/events
Body: CalendarEventCreate
Response: CalendarEventRead (201 Created)
Descripción: Crea un nuevo evento local
Validaciones:
  - google_event_id único
  - end_datetime > start_datetime
Errors:
  - 409 Conflict (google_event_id duplicado)
  - 400 Bad Request (fechas inválidas)
```

```http
PUT /api/v1/calendar/events/{id}
Body: CalendarEventUpdate (partial)
Response: CalendarEventRead
Descripción: Actualiza evento (solo campos enviados)
Validaciones: end_datetime > start_datetime
Errors: 404 Not Found, 400 Bad Request
```

```http
PATCH /api/v1/calendar/events/{id}
Body: CalendarEventUpdate (partial)
Response: CalendarEventRead
Descripción: Actualización parcial (idéntico a PUT)
```

```http
DELETE /api/v1/calendar/events/{id}
Response: {"message": "Event {id} deleted from cache"}
Descripción: Elimina evento de la BD local (NO de Google Calendar)
Errors: 404 Not Found
```

---

#### 🩺 Health Check

```http
GET /api/v1/calendar/health
Response: {
  "configured": bool,
  "calendar_id": str,
  "timezone": str,
  "credentials_file": str,
  "credentials_exist": bool,
  "service_initialized": bool,
  "message": str,
  "help": str (opcional)
}
Descripción: Verifica estado de configuración de Google Calendar
```

**Ejemplo de respuesta exitosa:**
```json
{
  "configured": true,
  "calendar_id": "tucotony1396@gmail.com",
  "timezone": "America/Lima",
  "credentials_file": "credentials/service-account.json",
  "credentials_exist": true,
  "service_initialized": true,
  "message": "✅ Google Calendar service is properly configured and ready to use"
}
```

---

### 3. Inbox Endpoints

```http
GET /api/v1/inbox
POST /api/v1/inbox
GET /api/v1/inbox/{id}
PUT /api/v1/inbox/{id}
DELETE /api/v1/inbox/{id}
```

(CRUD básico para InboxItems)

---

### 4. Ideas Endpoints

```http
GET /api/v1/ideas
POST /api/v1/ideas
GET /api/v1/ideas/{id}
PUT /api/v1/ideas/{id}
DELETE /api/v1/ideas/{id}
```

(CRUD básico para Ideas)

---

### 5. User, Status, Priority

Endpoints de catálogo (básicamente GET):

```http
GET /api/v1/users
GET /api/v1/statuses
GET /api/v1/priorities
```

---

## Servicios Externos

### Google Calendar API

**Archivo:** `services/google_calendar.py`

#### Configuración

Usa **Service Account authentication** (NO OAuth2):

**Variables de entorno:**
```bash
GOOGLE_SERVICE_ACCOUNT_FILE=credentials/service-account.json
GOOGLE_CALENDAR_ID=tucotony1396@gmail.com
GOOGLE_TIMEZONE=America/Lima
```

**Clase principal:**
```python
class GoogleCalendarService:
    def __init__(self):
        # Inicializa servicio con Service Account
        self.service = build('calendar', 'v3', credentials=creds)
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID")
        self.timezone = pytz.timezone(os.getenv("GOOGLE_TIMEZONE"))
```

#### Métodos principales

```python
get_today_events() -> List[dict]
get_week_events() -> List[dict]
get_month_events() -> List[dict]
get_critical_events(days_ahead: int) -> List[dict]
parse_event(google_event: dict) -> dict
```

#### Flujo de parse_event()

```python
def parse_event(google_event: dict) -> dict:
    """
    Convierte evento de Google Calendar a formato interno.
    
    Mapeo:
      - id → google_event_id
      - summary → summary
      - description → description
      - start.dateTime / start.date → start_datetime
      - end.dateTime / end.date → end_datetime
      - location → location
      - status → status
      - extendedProperties.private → extra_data
    """
```

**Manejo de fechas:**
- Eventos all-day: `start.date` (sin hora)
- Eventos con hora: `start.dateTime` (ISO 8601 con timezone)
- Conversión automática a timezone configurado

**Validación de errores:**
- Archivo de credenciales no encontrado → Error con path completo
- JSON inválido → Error de parsing
- API error → Error con detalles de Google

---

## Configuración y Deployment

### Variables de Entorno

**Archivo:** `.env` (ver `.env.example` para template)

#### Database Configuration

```bash
# Tipo de base de datos (sqlite o postgresql)
DB_TYPE=sqlite

# SQLite (default)
SQLITE_PATH=./db.sqlite3

# PostgreSQL (requerido si DB_TYPE=postgresql)
POSTGRES_USER=mnemos_user
POSTGRES_PASSWORD=tu_contraseña
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mnemos_db

# PostgreSQL - Configuración avanzada (opcional)
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

**Validación automática:**
- Si `DB_TYPE=postgresql` y faltan variables → Exit con mensaje de error
- Si `DB_TYPE` no es `sqlite` o `postgresql` → Exit con error
- Mensajes de error incluyen ejemplos de configuración correcta

---

#### Google Calendar Configuration

```bash
# Credenciales
GOOGLE_SERVICE_ACCOUNT_FILE=credentials/service-account.json

# Configuración del calendario
GOOGLE_CALENDAR_ID=tucotony1396@gmail.com
GOOGLE_TIMEZONE=America/Lima
```

**Nota:** Ver `docs/CALENDAR_SETUP.md` para setup inicial de Service Account.

---

#### Application Configuration

```bash
# Usuario por defecto (single-user app)
DEFAULT_USER_ID=1

# Logging
LOG_LEVEL=INFO
```

---

### Instalación y Setup

#### Requisitos previos
- Python 3.11+
- uv (package manager)
- PostgreSQL 14+ (opcional, para producción)
- Google Cloud Project con Calendar API habilitada

#### Pasos de instalación

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd mnemos

# 2. Instalar dependencias con uv
uv sync

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# 4. (Opcional) Setup Google Calendar
# Ver docs/CALENDAR_SETUP.md para crear Service Account

# 5. Iniciar servidor
uv run uvicorn main:app --reload

# 6. Verificar
curl http://localhost:8000/api/v1/calendar/health
```

---

### Deployment

#### Development (SQLite)

```bash
# .env
DB_TYPE=sqlite
SQLITE_PATH=./db.sqlite3

# Iniciar
uv run uvicorn main:app --reload --port 8000
```

#### Production (PostgreSQL)

```bash
# .env
DB_TYPE=postgresql
POSTGRES_USER=mnemos_prod
POSTGRES_PASSWORD=<secure-password>
POSTGRES_HOST=db.example.com
POSTGRES_PORT=5432
POSTGRES_DB=mnemos_production

# Iniciar con Gunicorn
uv run gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

#### Docker (futuro)

```bash
# TODO: Crear Dockerfile y docker-compose.yml
docker-compose up -d
```

Ver `docs/DATABASE_SETUP.md` para opciones de deployment (Supabase, Neon, Railway).

---

## Decisiones de Diseño

### 1. Single-User Application

**Decisión:** Todos los `user_id` son **nullable** (opcionales).

**Razón:**
- El sistema es para un único usuario
- No requiere autenticación compleja
- Se usa `DEFAULT_USER_ID` desde `.env` cuando sea necesario
- Permite flexibilidad futura para multi-usuario sin cambios de esquema

**Implementación:**
```python
# En modelos
user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

# En startup
DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID")
```

---

### 2. Database Configuration (DB_TYPE)

**Decisión:** Una variable `DB_TYPE` controla SQLite vs PostgreSQL.

**Razón:**
- Simplicidad: cambiar de BD con 1 variable
- Developer Experience: SQLite local, PostgreSQL en prod
- Validación automática de configuración requerida
- Mensajes de error claros y accionables

**Alternativas consideradas:**
- ❌ Connection strings completas → Menos user-friendly
- ❌ Auto-detección → Menos explícito, posible confusión

---

### 3. Google Calendar: Service Account (no OAuth2)

**Decisión:** Usar Service Account authentication.

**Razón:**
- Single-user app → No necesita OAuth flow
- Más simple de configurar (un archivo JSON)
- No requiere browser para autenticación
- Ideal para scripts/servicios automatizados

**Limitaciones:**
- Requiere compartir calendario con service account email
- No permite acceso a calendarios privados de otros usuarios

---

### 4. CalendarEvent: `extra_data` (no `metadata`)

**Decisión:** Renombrar campo de `metadata` a `extra_data`.

**Razón:**
- `metadata` es palabra reservada en SQLAlchemy
- Causa conflictos con `Base.metadata`
- `extra_data` es más descriptivo y evita problemas

---

### 5. Búsqueda Case-Insensitive

**Decisión:** Usar `ILIKE` (PostgreSQL) / `LIKE` case-insensitive (SQLite).

**Razón:**
- UX: búsqueda más amigable ("gym" encuentra "GYM")
- Compatible con ambas bases de datos
- Performance aceptable para volumen de eventos personal

**Implementación:**
```python
CalendarEvent.summary.ilike(f"%{search}%")
```

---

### 6. Validación de Fechas en Updates

**Decisión:** Validar `end_datetime > start_datetime` en 3 casos:
1. Ambas fechas provistas
2. Solo `end_datetime` (comparar con `start_datetime` existente)
3. Solo `start_datetime` (comparar con `end_datetime` existente)

**Razón:**
- Prevenir datos inconsistentes
- Mensajes de error claros
- Validación en backend (no depender de frontend)

**Nota técnica:**
- SQLAlchemy ORM devuelve Python datetimes, no ColumnElements
- Usar `# type: ignore` para satisfacer type checker

---

### 7. Sync Strategy: Upsert

**Decisión:** Al sincronizar desde Google Calendar:
- Si evento existe (por `google_event_id`) → **UPDATE**
- Si no existe → **INSERT**

**Razón:**
- Evita duplicados
- Mantiene metadata local (category, priority) al resincronizar
- Actualiza cambios de Google Calendar automáticamente

**Implementación:**
```python
existing = db.query(CalendarEvent).filter(
    CalendarEvent.google_event_id == parsed_event["google_event_id"]
).first()

if existing:
    for key, value in parsed_event.items():
        if key != "google_event_id":
            setattr(existing, key, value)
else:
    db_event = CalendarEvent(**parsed_event)
    db.add(db_event)
```

---

### 8. Error Messages: Detallados y Accionables

**Decisión:** Todos los errores incluyen:
- ❌ Qué salió mal
- 💡 Cómo solucionarlo
- 📚 Dónde encontrar más info (link a docs)

**Ejemplo:**
```
❌ ERROR: Variable de entorno 'POSTGRES_USER' requerida para DB_TYPE=postgresql
💡 Solución: Agrega 'POSTGRES_USER' a tu archivo .env

Ejemplo en .env:
DB_TYPE=postgresql
POSTGRES_USER=mnemos_user
...

📚 Ver docs/DATABASE_SETUP.md para más información
```

**Razón:**
- Developer Experience
- Reducir tiempo de debugging
- Auto-documentación del sistema

---

## Schemas (Pydantic)

### CalendarEventCreate
```python
class CalendarEventCreate(BaseModel):
    google_event_id: str          # requerido
    summary: str                  # requerido
    start_datetime: datetime      # requerido
    end_datetime: datetime        # requerido
    description: str = ""
    location: str | None = None
    all_day: bool = False
    category: str | None = None   # TRABAJO, SALUD, OCIO, RUTINA
    priority: str | None = None   # low, medium, high, critical
    extra_data: dict = {}
```

### CalendarEventUpdate
```python
class CalendarEventUpdate(BaseModel):
    summary: str | None = None
    description: str | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    location: str | None = None
    category: str | None = None
    priority: str | None = None
    extra_data: dict | None = None
    
    # Todos los campos son opcionales
```

### CalendarEventRead
```python
class CalendarEventRead(BaseModel):
    # Todos los campos del modelo (full detail)
    id: int
    google_event_id: str
    summary: str
    description: str
    location: str | None
    start_datetime: datetime
    end_datetime: datetime
    all_day: bool
    status: str | None
    priority: str | None
    category: str | None
    extra_data: dict
    user_id: int | None
    created_at: datetime
    updated_at: datetime
    synced_at: datetime | None
```

### CalendarEventSummary
```python
class CalendarEventSummary(BaseModel):
    # Vista resumida (para listados)
    id: int
    google_event_id: str
    summary: str
    start_datetime: datetime
    end_datetime: datetime
    all_day: bool
    priority: str | None
    category: str | None
```

---

## Testing

### Estado actual
⚠️ **Tests no implementados** (TODO para v1.1)

### Tests propuestos

```bash
tests/
├── test_database.py           # Conexión, validación
├── test_calendar_crud.py      # CRUD de eventos
├── test_calendar_sync.py      # Sincronización con Google
├── test_filters.py            # Búsqueda y filtros
├── test_validations.py        # Validaciones de fecha, duplicados
└── test_google_service.py     # Mock de Google Calendar API
```

### Ejecutar tests (futuro)
```bash
uv run pytest tests/ -v
uv run pytest tests/test_calendar_crud.py::test_create_event
```

---

## Logging

**Librería:** `rich` (colorful terminal output)

**Archivo:** `utils/logger.py`

```python
from rich.logging import RichHandler
import logging

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("mnemos")
```

**Uso:**
```python
from utils.logger import logger

logger.info("✅ Event created successfully")
logger.warning("⚠️  Google Calendar not configured")
logger.error("❌ Failed to sync events")
```

---

## Próximos Pasos

### Roadmap v1.1 - v1.3

#### v1.1: Testing & Reliability
- [ ] Tests unitarios (pytest)
- [ ] Tests de integración con Google Calendar (mocked)
- [ ] CI/CD con GitHub Actions
- [ ] Pre-commit hooks (ruff, black, mypy)

#### v1.2: Telegram Integration
- [ ] Bot de Telegram para consultas rápidas
- [ ] Comandos: `/today`, `/week`, `/add <event>`
- [ ] Notificaciones de eventos próximos
- [ ] Integración orgánica (sin spam)

#### v1.3: Sync Bidireccional
- [ ] Crear eventos en Google Calendar desde la API
- [ ] Actualizar eventos de Google Calendar
- [ ] Eliminar eventos de Google Calendar
- [ ] Webhook para cambios en Google Calendar

### Features Futuras (v2.0+)

#### Frontend
- [ ] NiceGUI dashboard
- [ ] Streamlit analytics
- [ ] Vista semanal/mensual interactiva
- [ ] Drag-and-drop para categorización

#### Analytics
- [ ] Tiempo por categoría (TRABAJO, SALUD, etc.)
- [ ] Gráficos de distribución de tiempo
- [ ] Reportes semanales/mensuales
- [ ] Sugerencias de optimización

#### Integrations
- [ ] Notion export
- [ ] iCal/CSV export
- [ ] Apple Calendar sync
- [ ] Slack notifications

#### Docker & Deployment
- [ ] Dockerfile
- [ ] docker-compose.yml (con PostgreSQL)
- [ ] Terraform para cloud deployment
- [ ] Health checks y monitoring

---

## Troubleshooting

### Error: "DB_TYPE no es válido"
**Solución:** Verifica que `.env` tenga `DB_TYPE=sqlite` o `DB_TYPE=postgresql`

### Error: "POSTGRES_USER requerido"
**Solución:** Si usas PostgreSQL, agrega todas las variables `POSTGRES_*` a `.env`

### Error: "Google Calendar service not configured"
**Solución:** 
1. Verifica que `credentials/service-account.json` existe
2. Corre `GET /api/v1/calendar/health` para diagnóstico
3. Ver `docs/CALENDAR_SETUP.md`

### Error: "end_datetime must be after start_datetime"
**Solución:** Verifica que la fecha de fin sea posterior a la de inicio

### Error: "Event with google_event_id already exists"
**Solución:** Usa un `google_event_id` diferente o actualiza el evento existente

---

## Contacto y Contribuciones

**Autor:** @constant1n396  
**Proyecto:** Personal time management (single-user)  
**Estado:** MVP v1.0 (funcional y robusto)  

Para bugs, features o preguntas, contactar al autor.

---

## Apéndice: Comandos Útiles

```bash
# Iniciar servidor de desarrollo
uv run uvicorn main:app --reload

# Iniciar con logs detallados
uv run uvicorn main:app --reload --log-level debug

# Acceder a documentación interactiva
open http://localhost:8000/docs

# Verificar salud de Google Calendar
curl http://localhost:8000/api/v1/calendar/health

# Sincronizar eventos de hoy
curl -X POST http://localhost:8000/api/v1/calendar/sync/today

# Listar eventos
curl "http://localhost:8000/api/v1/calendar/events?category=TRABAJO"

# Buscar eventos
curl "http://localhost:8000/api/v1/calendar/events?search=gym"

# Crear evento
curl -X POST http://localhost:8000/api/v1/calendar/events \
  -H "Content-Type: application/json" \
  -d '{
    "google_event_id": "local_001",
    "summary": "Test Event",
    "start_datetime": "2026-02-21T10:00:00",
    "end_datetime": "2026-02-21T11:00:00",
    "category": "TRABAJO"
  }'

# Actualizar prioridad
curl -X PATCH http://localhost:8000/api/v1/calendar/events/1 \
  -H "Content-Type: application/json" \
  -d '{"priority": "critical"}'

# Python shell interactivo
uv run python
>>> from database import SessionLocal
>>> from models.calendar_event import CalendarEvent
>>> db = SessionLocal()
>>> events = db.query(CalendarEvent).all()
```

---

**Fin del documento técnico**

*Última actualización: 2026-02-20*
*Versión: 1.0 (MVP)*
