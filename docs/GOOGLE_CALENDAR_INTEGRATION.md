# Google Calendar Integration

## Descripción General

La integración con Google Calendar permite sincronizar eventos del calendario externo hacia la base de datos local de **mnemos**, facilitando la gestión unificada del tiempo y tareas.

## Arquitectura

```
┌─────────────────────┐
│  Google Calendar    │
│   API (Cloud)       │
└──────────┬──────────┘
           │
           │ Service Account Auth
           │ (JSON credentials)
           │
           ▼
┌─────────────────────────────────────────┐
│  GoogleCalendarService                  │
│  (services/google_calendar.py)          │
│                                         │
│  • Authenticate with Service Account   │
│  • Fetch events by timeframe           │
│  • Parse BUJO_META from descriptions   │
│  • Map to CalendarEvent schema         │
└──────────┬──────────────────────────────┘
           │
           │ Events Data
           │
           ▼
┌─────────────────────────────────────────┐
│  Calendar Router                        │
│  (routers/calendar.py)                  │
│                                         │
│  POST /sync/today                       │
│  POST /sync/week                        │
│  POST /sync/month                       │
│  POST /sync/critical                    │
│  GET  /events                           │
│  GET  /events/{id}                      │
│  DELETE /events/{id}                    │
└──────────┬──────────────────────────────┘
           │
           │ ORM Operations
           │
           ▼
┌─────────────────────────────────────────┐
│  SQLite Database                        │
│                                         │
│  calendar_events table                  │
│  • Cached events                        │
│  • Metadata (category, priority)       │
│  • Timestamps (synced_at)              │
└─────────────────────────────────────────┘
```

## Flujo de Datos

### 1. Sincronización (Sync Flow)

```
Usuario hace request POST /api/v1/calendar/sync/today
                 │
                 ▼
    ┌───────────────────────────┐
    │  Calendar Router          │
    │  • Validate request       │
    │  • Call service method    │
    └───────────┬───────────────┘
                │
                ▼
    ┌───────────────────────────────────────┐
    │  GoogleCalendarService                │
    │  1. Authenticate with Service Account │
    │  2. Calculate time range (today)      │
    │  3. Call Calendar API                 │
    │  4. Parse events                      │
    │  5. Extract BUJO_META                 │
    └───────────┬───────────────────────────┘
                │
                ▼
    ┌───────────────────────────┐
    │  Database Operations      │
    │  • Upsert events          │
    │  • Update synced_at       │
    │  • Return saved events    │
    └───────────┬───────────────┘
                │
                ▼
            Response JSON
```

### 2. Consulta de Eventos Cacheados (Query Flow)

```
Usuario hace request GET /api/v1/calendar/events?category=TRABAJO
                 │
                 ▼
    ┌───────────────────────────┐
    │  Calendar Router          │
    │  • Apply filters          │
    │  • Query database         │
    └───────────┬───────────────┘
                │
                ▼
    ┌───────────────────────────┐
    │  SQLite Query             │
    │  SELECT * FROM            │
    │  calendar_events          │
    │  WHERE category='TRABAJO' │
    └───────────┬───────────────┘
                │
                ▼
            Response JSON
```

## Configuración

### 1. Service Account Setup

Para usar la autenticación por Service Account (sin OAuth2):

1. **Crear Service Account en Google Cloud Console:**
   - Ir a [Google Cloud Console](https://console.cloud.google.com)
   - Crear proyecto o seleccionar existente
   - Habilitar "Google Calendar API"
   - Crear Service Account
   - Descargar archivo JSON de credenciales

2. **Compartir calendario con Service Account:**
   - Abrir Google Calendar
   - Ir a configuración del calendario que deseas sincronizar
   - En "Compartir con personas específicas", agregar el email del Service Account (formato: `nombre@proyecto.iam.gserviceaccount.com`)
   - Dar permisos de "Ver todos los detalles de eventos"

3. **Colocar credenciales:**
   ```bash
   mkdir -p credentials
   # Copiar archivo JSON descargado
   cp ~/Downloads/skilful-webbing-*.json credentials/service-account.json
   ```

### 2. Variables de Entorno

Actualizar `.env` con:

```bash
# Google Calendar Configuration
GOOGLE_SERVICE_ACCOUNT_FILE=credentials/service-account.json
GOOGLE_CALENDAR_ID=tucotony1396@gmail.com  # Tu email de Google Calendar
TIMEZONE=America/Lima
```

### 3. Instalación de Dependencias

```bash
uv sync
```

Esto instalará:
- `google-auth`
- `google-auth-oauthlib`
- `google-auth-httplib2`
- `google-api-python-client`

## Formato BUJO_META

Para agregar metadata a eventos en Google Calendar, incluye en la **descripción** del evento:

```
BUJO_META: {"status": "in-progress", "category": "TRABAJO", "priority": "high"}
```

### Categorías Soportadas
- `TRABAJO` - Actividades laborales
- `SALUD` - Ejercicio, citas médicas
- `OCIO` - Entretenimiento, hobbies
- `RUTINA` - Tareas diarias recurrentes

### Prioridades Soportadas
- `low` - Prioridad baja
- `medium` - Prioridad media
- `high` - Prioridad alta
- `critical` - Crítico/urgente

### Ejemplo de Evento en Google Calendar

**Título:** Reunión con equipo de desarrollo

**Descripción:**
```
Revisar avances del sprint actual y planificar próximas tareas.

BUJO_META: {"category": "TRABAJO", "priority": "high", "status": "pending"}
```

**Hora:** 2026-02-20 10:00 - 11:00

## Endpoints de la API

### Sincronización

#### 1. Sincronizar eventos del día
```http
POST /api/v1/calendar/sync/today
```

**Response:**
```json
{
  "synced_count": 3,
  "events": [
    {
      "id": 1,
      "google_event_id": "abc123",
      "summary": "Reunión con equipo",
      "start_datetime": "2026-02-20T10:00:00-05:00",
      "end_datetime": "2026-02-20T11:00:00-05:00",
      "category": "TRABAJO",
      "priority": "high"
    }
  ]
}
```

#### 2. Sincronizar eventos de la semana
```http
POST /api/v1/calendar/sync/week
```

#### 3. Sincronizar eventos del mes
```http
POST /api/v1/calendar/sync/month
```

#### 4. Sincronizar eventos críticos próximos
```http
POST /api/v1/calendar/sync/critical?days_ahead=7
```

Parámetros:
- `days_ahead` (opcional): Número de días hacia adelante (default: 7)

### Consulta de Eventos Cacheados

#### 1. Listar eventos
```http
GET /api/v1/calendar/events?category=TRABAJO&priority=high&skip=0&limit=50
```

**Query Parameters:**
- `category` (opcional): Filtrar por categoría
- `priority` (opcional): Filtrar por prioridad
- `skip` (opcional): Offset para paginación (default: 0)
- `limit` (opcional): Límite de resultados (default: 50)

**Response:**
```json
[
  {
    "id": 1,
    "summary": "Reunión con equipo",
    "start_datetime": "2026-02-20T10:00:00-05:00",
    "end_datetime": "2026-02-20T11:00:00-05:00",
    "category": "TRABAJO",
    "priority": "high"
  }
]
```

#### 2. Obtener evento específico
```http
GET /api/v1/calendar/events/1
```

**Response:**
```json
{
  "id": 1,
  "google_event_id": "abc123",
  "summary": "Reunión con equipo",
  "description": "Revisar avances...",
  "location": "Sala de conferencias",
  "start_datetime": "2026-02-20T10:00:00-05:00",
  "end_datetime": "2026-02-20T11:00:00-05:00",
  "all_day": false,
  "status": "pending",
  "priority": "high",
  "category": "TRABAJO",
  "metadata": {"custom_field": "value"},
  "created_at": "2026-02-20T08:00:00",
  "updated_at": "2026-02-20T08:00:00",
  "synced_at": "2026-02-20T08:00:00"
}
```

#### 3. Eliminar evento del cache
```http
DELETE /api/v1/calendar/events/1
```

**Response:**
```json
{
  "message": "Event deleted successfully"
}
```

## Modelo de Datos

### CalendarEvent (models/calendar_event.py)

```python
class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    
    id: int                      # Primary key
    google_event_id: str         # ID único de Google Calendar
    summary: str                 # Título del evento
    description: str | None      # Descripción completa
    location: str | None         # Ubicación
    start_datetime: datetime     # Inicio (timezone-aware)
    end_datetime: datetime       # Fin (timezone-aware)
    all_day: bool               # Es evento de todo el día
    status: str | None          # Estado del evento
    priority: str | None        # Prioridad (low/medium/high/critical)
    category: str | None        # Categoría (TRABAJO/SALUD/OCIO/RUTINA)
    metadata: dict | None       # JSON con metadata adicional
    created_at: datetime        # Timestamp de creación
    updated_at: datetime        # Timestamp de última actualización
    synced_at: datetime         # Timestamp de última sincronización
```

### Índices

Para optimizar consultas:
- `ix_calendar_events_google_event_id` - Búsqueda rápida por ID de Google
- `ix_calendar_events_start_datetime` - Ordenamiento por fecha
- `ix_calendar_events_category` - Filtrado por categoría
- `ix_calendar_events_priority` - Filtrado por prioridad

## Manejo de Timezone

Todos los eventos se almacenan con **timezone-aware datetimes** usando la zona configurada en `.env` (America/Lima).

El servicio maneja automáticamente:
- Conversión de eventos de Google Calendar a timezone local
- Fechas all-day (eventos de todo el día)
- Comparaciones de fecha/hora para filtros (today, week, month)

## Estrategia de Cache

### Upsert Logic

El sistema usa **upsert** (insert or update):

1. Si el `google_event_id` no existe → **INSERT** nuevo evento
2. Si el `google_event_id` existe → **UPDATE** evento existente

Esto permite:
- Sincronizaciones repetidas sin duplicados
- Actualización automática de eventos modificados en Google Calendar
- Mantener metadata local (categorías, prioridades)

### Timestamp de Sincronización

Cada evento tiene `synced_at` que registra cuándo fue la última sincronización. Útil para:
- Detectar eventos desactualizados
- Implementar limpieza automática de eventos antiguos
- Auditoría de sincronizaciones

## Testing

### 1. Verificar Configuración

```bash
# Verificar que el archivo de credenciales existe
ls -la credentials/service-account.json

# Verificar variables de entorno
cat .env | grep GOOGLE
```

### 2. Iniciar Servidor

```bash
uv run uvicorn main:app --reload
```

### 3. Test Manual con curl

```bash
# Sincronizar eventos de hoy
curl -X POST http://localhost:8000/api/v1/calendar/sync/today

# Listar eventos cacheados
curl http://localhost:8000/api/v1/calendar/events

# Filtrar por categoría
curl "http://localhost:8000/api/v1/calendar/events?category=TRABAJO"
```

### 4. Test desde Swagger UI

Abrir navegador en: `http://localhost:8000/docs`

## Solución de Problemas

### Error: "Service account credentials not found"

**Causa:** Archivo de credenciales no existe o ruta incorrecta

**Solución:**
```bash
# Verificar ruta en .env
echo $GOOGLE_SERVICE_ACCOUNT_FILE

# Verificar que archivo existe
ls credentials/service-account.json
```

### Error: "Calendar not found" o "403 Forbidden"

**Causa:** El Service Account no tiene acceso al calendario

**Solución:**
1. Abrir Google Calendar
2. Ir a configuración del calendario
3. Compartir con el email del Service Account
4. Dar permisos de lectura

### Error: "Invalid timezone"

**Causa:** Timezone en `.env` no es válido

**Solución:**
```bash
# Verificar timezone válido
python3 -c "import zoneinfo; print(zoneinfo.ZoneInfo('America/Lima'))"

# Lista de timezones válidos
python3 -c "import zoneinfo; print(sorted(zoneinfo.available_timezones()))"
```

### Eventos no se sincronizan

**Diagnóstico:**
1. Verificar logs del servidor
2. Verificar que el calendario tenga eventos en el rango de fechas
3. Verificar que `GOOGLE_CALENDAR_ID` sea correcto

```bash
# Ver logs detallados
uv run uvicorn main:app --reload --log-level debug
```

## Mejoras Futuras

### Corto Plazo
- [ ] Sincronización automática periódica (background task)
- [ ] Webhook de Google Calendar para actualizaciones en tiempo real
- [ ] Endpoint para buscar eventos por texto
- [ ] Estadísticas (eventos por categoría, eventos esta semana)

### Mediano Plazo
- [ ] Escribir eventos desde mnemos hacia Google Calendar
- [ ] Actualizar categorías/prioridades en Google Calendar
- [ ] Integración bidireccional completa

### Largo Plazo
- [ ] Sugerencias automáticas de categoría usando metadata histórica
- [ ] Detección de conflictos de horario
- [ ] Visualización de calendario en frontend (nicegui/streamlit)

## Referencias

- [Google Calendar API Documentation](https://developers.google.com/calendar/api/guides/overview)
- [Service Account Authentication](https://developers.google.com/identity/protocols/oauth2/service-account)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/latest/)
