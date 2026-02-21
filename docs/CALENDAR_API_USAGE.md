# Calendar Events API - Guía de Uso

Esta guía muestra cómo usar los endpoints de gestión de eventos del calendario.

## 🎨 Categorías y Colores en Google Calendar

Mnemos asigna automáticamente colores a los eventos según su categoría cuando se sincronizan con Google Calendar. Esto permite una organización visual clara.

### Categorías Disponibles

| Categoría | Color | Descripción |
|-----------|-------|-------------|
| `TRABAJO` | 🔵 Azul (Arándano) | Trabajo, reuniones, tareas profesionales |
| `SALUD` | 🟢 Verde (Albahaca) | Ejercicio, citas médicas, bienestar |
| `OCIO` | 🔴 Rojo (Tomate) | Entretenimiento, hobbies, diversión |
| `RUTINA` | 🟡 Amarillo (Banana) | Tareas diarias, hábitos |
| `PERSONAL` | 💜 Lavanda | Asuntos personales |
| `ESTUDIO` | 🔷 Cyan (Pavo real) | Aprendizaje, cursos, lectura |
| `FAMILIA` | 🌸 Rosado (Flamingo) | Eventos familiares |
| `SOCIAL` | 🟣 Púrpura (Uva) | Eventos sociales, amigos |
| `SIN_CATEGORIA` | ⚫ Gris (Grafito) | Sin categoría asignada |

### Obtener Categorías Disponibles

```bash
GET /api/v1/calendar/categories
```

**Response:**
```json
{
  "TRABAJO": {
    "color_id": "9",
    "color_name": "Arándano"
  },
  "SALUD": {
    "color_id": "10",
    "color_name": "Albahaca"
  },
  ...
}
```

### Cómo Funciona

1. **Creas un evento local** asignándole una categoría (ej: `"category": "TRABAJO"`)
2. **Sincronizas con Google Calendar** usando `POST /events/{id}/push`
3. **Google Calendar recibe el colorId** correspondiente automáticamente
4. **El evento aparece con el color** asignado en tu calendario

### Ejemplo de Uso

```bash
# 1. Crear evento con categoría TRABAJO
curl -X POST http://localhost:8000/api/v1/calendar/events \
  -H "Content-Type: application/json" \
  -d '{
    "google_event_id": "local_reunion_001",
    "summary": "Reunión de equipo",
    "category": "TRABAJO",
    "start_datetime": "2026-02-21T10:00:00",
    "end_datetime": "2026-02-21T11:00:00"
  }'

# 2. Sincronizar con Google Calendar (se aplicará color AZUL)
curl -X POST http://localhost:8000/api/v1/calendar/events/1/push

# 3. Filtrar eventos por categoría
curl "http://localhost:8000/api/v1/calendar/events?category=TRABAJO"
```

---

## Endpoints Disponibles

### 📋 Consulta

- `GET /api/v1/calendar/events` - Listar eventos (con filtros)
- `GET /api/v1/calendar/events/{id}` - Obtener evento específico
- `GET /api/v1/calendar/health` - Verificar configuración de Google Calendar

### 🔄 Sincronización (Google Calendar)

- `POST /api/v1/calendar/sync/today` - Sincronizar eventos de hoy
- `POST /api/v1/calendar/sync/week` - Sincronizar eventos de la semana
- `POST /api/v1/calendar/sync/month` - Sincronizar eventos del mes
- `POST /api/v1/calendar/sync/critical?days_ahead=7` - Sincronizar próximos eventos

### ✏️ Gestión de Eventos (NUEVO)

- `POST /api/v1/calendar/events` - Crear nuevo evento
- `PUT /api/v1/calendar/events/{id}` - Actualizar evento completo
- `PATCH /api/v1/calendar/events/{id}` - Actualizar evento parcialmente
- `DELETE /api/v1/calendar/events/{id}` - Eliminar evento

---

## Ejemplos de Uso

### 1. Crear un Evento

**Request:**
```bash
POST /api/v1/calendar/events
Content-Type: application/json

{
  "google_event_id": "local_event_001",
  "summary": "Reunión con cliente",
  "description": "Revisar propuesta comercial",
  "start_datetime": "2026-02-21T10:00:00-05:00",
  "end_datetime": "2026-02-21T11:00:00-05:00",
  "all_day": false,
  "category": "TRABAJO",
  "priority": "high",
  "location": "Oficina principal",
  "extra_data": {
    "attendees": 3,
    "room": "Sala 2"
  }
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "google_event_id": "local_event_001",
  "summary": "Reunión con cliente",
  "description": "Revisar propuesta comercial",
  "location": "Oficina principal",
  "start_datetime": "2026-02-21T10:00:00-05:00",
  "end_datetime": "2026-02-21T11:00:00-05:00",
  "all_day": false,
  "status": null,
  "priority": "high",
  "category": "TRABAJO",
  "extra_data": {
    "attendees": 3,
    "room": "Sala 2"
  },
  "created_at": "2026-02-20T21:00:00",
  "updated_at": "2026-02-20T21:00:00",
  "synced_at": "2026-02-20T21:00:00"
}
```

**Con curl:**
```bash
curl -X POST http://localhost:8000/api/v1/calendar/events \
  -H "Content-Type: application/json" \
  -d '{
    "google_event_id": "local_event_001",
    "summary": "Reunión con cliente",
    "start_datetime": "2026-02-21T10:00:00-05:00",
    "end_datetime": "2026-02-21T11:00:00-05:00",
    "category": "TRABAJO",
    "priority": "high"
  }'
```

> **💡 Nota:** Al asignar `"category": "TRABAJO"`, cuando sincronices este evento con Google Calendar usando `POST /events/{id}/push`, automáticamente se le asignará el color **Azul (Arándano)** para identificación visual rápida.

### 2. Listar Eventos con Filtros

**Todos los eventos:**
```bash
GET /api/v1/calendar/events
```

**Solo eventos de TRABAJO (🔵 Azul en Google Calendar):**
```bash
GET /api/v1/calendar/events?category=TRABAJO
```

**Solo eventos de SALUD (🟢 Verde en Google Calendar):**
```bash
GET /api/v1/calendar/events?category=SALUD
```

**Solo eventos de OCIO (🔴 Rojo en Google Calendar):**
```bash
GET /api/v1/calendar/events?category=OCIO
```

**Eventos de prioridad alta:**
```bash
GET /api/v1/calendar/events?priority=high
```

**Buscar por texto (case-insensitive):**
```bash
GET /api/v1/calendar/events?search=gym
# Busca en título y descripción
```

**Filtrar por rango de fechas:**
```bash
GET /api/v1/calendar/events?start_date=2026-02-20T00:00:00&end_date=2026-02-28T23:59:59
# Muestra eventos entre estas fechas
```

**Combinado - múltiples filtros:**
```bash
GET /api/v1/calendar/events?category=SALUD&search=gym&priority=high&skip=0&limit=10
```

**Con curl:**
```bash
# Filtro por categoría (verás eventos con color específico en Google Calendar)
curl "http://localhost:8000/api/v1/calendar/events?category=TRABAJO"

# Filtro por categoría y prioridad
curl "http://localhost:8000/api/v1/calendar/events?category=TRABAJO&priority=high"

# Búsqueda por texto
curl "http://localhost:8000/api/v1/calendar/events?search=reunion"

# Rango de fechas
curl "http://localhost:8000/api/v1/calendar/events?start_date=2026-02-20T00:00:00&end_date=2026-02-28T23:59:59"

# Combinado
curl "http://localhost:8000/api/v1/calendar/events?category=TRABAJO&search=cliente&start_date=2026-02-20T00:00:00"
```

### 3. Obtener Evento Específico

**Request:**
```bash
GET /api/v1/calendar/events/1
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "google_event_id": "local_event_001",
  "summary": "Reunión con cliente",
  "start_datetime": "2026-02-21T10:00:00-05:00",
  "end_datetime": "2026-02-21T11:00:00-05:00",
  "category": "TRABAJO",
  "priority": "high"
}
```

### 4. Actualizar Evento (PUT - Actualización Completa)

**Request:**
```bash
PUT /api/v1/calendar/events/1
Content-Type: application/json

{
  "summary": "Reunión con cliente - CONFIRMADA",
  "description": "Propuesta aprobada. Firmar contrato.",
  "priority": "critical",
  "category": "TRABAJO"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "summary": "Reunión con cliente - CONFIRMADA",
  "description": "Propuesta aprobada. Firmar contrato.",
  "priority": "critical",
  "category": "TRABAJO",
  "updated_at": "2026-02-20T21:15:00"
}
```

**Con curl:**
```bash
curl -X PUT http://localhost:8000/api/v1/calendar/events/1 \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "Reunión CONFIRMADA",
    "priority": "critical"
  }'
```

### 5. Actualizar Parcialmente (PATCH)

Actualizar solo un campo:

```bash
PATCH /api/v1/calendar/events/1
Content-Type: application/json

{
  "priority": "low"
}
```

**Con curl:**
```bash
curl -X PATCH http://localhost:8000/api/v1/calendar/events/1 \
  -H "Content-Type: application/json" \
  -d '{"priority": "low"}'
```

### 6. Eliminar Evento

**Request:**
```bash
DELETE /api/v1/calendar/events/1
```

**Response:** `200 OK`
```json
{
  "message": "Event 1 deleted from cache"
}
```

**Con curl:**
```bash
curl -X DELETE http://localhost:8000/api/v1/calendar/events/1
```

---

## Categorías Válidas

- `TRABAJO` - Actividades laborales
- `SALUD` - Ejercicio, citas médicas
- `OCIO` - Entretenimiento, hobbies
- `RUTINA` - Tareas diarias recurrentes

## Prioridades Válidas

- `low` - Prioridad baja
- `medium` - Prioridad media
- `high` - Prioridad alta
- `critical` - Crítico/urgente

## Campos Requeridos

### Para crear un evento:
- ✅ `google_event_id` - ID único (ej: "local_event_001")
- ✅ `summary` - Título del evento
- ✅ `start_datetime` - Fecha/hora de inicio (ISO 8601)
- ✅ `end_datetime` - Fecha/hora de fin (ISO 8601)

### Campos opcionales:
- `description` - Descripción detallada
- `location` - Ubicación del evento
- `category` - Categoría (TRABAJO, SALUD, etc.)
- `priority` - Prioridad (low, medium, high, critical)
- `all_day` - Es evento de todo el día (default: false)
- `extra_data` - Metadata adicional (JSON)

## Validaciones

### ✅ Búsqueda por texto (NUEVO)
- Busca en los campos `summary` y `description`
- **Case-insensitive** (no distingue mayúsculas/minúsculas)
- Soporta búsqueda parcial (ej: "gym" encuentra "GYM", "Gymnasium", "gym class")

**Ejemplos:**
```bash
# Buscar eventos relacionados con "reunión"
GET /api/v1/calendar/events?search=reunion

# Buscar eventos con "cliente" y categoría TRABAJO
GET /api/v1/calendar/events?search=cliente&category=TRABAJO
```

### ✅ Filtro por rango de fechas (NUEVO)
- `start_date`: Muestra eventos que **comienzan** desde esta fecha
- `end_date`: Muestra eventos que **terminan** hasta esta fecha
- Formato ISO 8601: `2026-02-20T00:00:00`

**Ejemplos:**
```bash
# Eventos de hoy
GET /api/v1/calendar/events?start_date=2026-02-20T00:00:00&end_date=2026-02-20T23:59:59

# Eventos de esta semana
GET /api/v1/calendar/events?start_date=2026-02-20T00:00:00&end_date=2026-02-27T23:59:59

# Eventos desde hoy en adelante
GET /api/v1/calendar/events?start_date=2026-02-20T00:00:00
```

### ✅ Validación de fechas
- `end_datetime` debe ser posterior a `start_datetime`
- Si se actualiza una fecha, se valida automáticamente

### ✅ Validación de duplicados
- No se pueden crear dos eventos con el mismo `google_event_id`
- Error 409 Conflict si ya existe

### ✅ Validación de existencia
- Error 404 Not Found si el evento no existe al actualizar/eliminar

## Errores Comunes

### 400 Bad Request
```json
{
  "detail": "end_datetime must be after start_datetime"
}
```
**Solución:** Verifica que la fecha de fin sea posterior a la de inicio.

### 404 Not Found
```json
{
  "detail": "Event not found"
}
```
**Solución:** Verifica que el ID del evento sea correcto.

### 409 Conflict
```json
{
  "detail": "Event with google_event_id 'local_event_001' already exists"
}
```
**Solución:** Usa un `google_event_id` diferente o actualiza el evento existente.

### 503 Service Unavailable
```json
{
  "detail": "Google Calendar service not configured"
}
```
**Solución:** Configura Google Calendar según `CALENDAR_SETUP.md`.

---

## Workflow Recomendado

### Para eventos locales (sin Google Calendar):

1. **Crear evento:**
   ```bash
   POST /api/v1/calendar/events
   ```

2. **Listar eventos:**
   ```bash
   GET /api/v1/calendar/events?category=TRABAJO
   ```

3. **Actualizar evento:**
   ```bash
   PUT /api/v1/calendar/events/{id}
   ```

4. **Eliminar evento:**
   ```bash
   DELETE /api/v1/calendar/events/{id}
   ```

### Para eventos de Google Calendar:

1. **Sincronizar desde Google:**
   ```bash
   POST /api/v1/calendar/sync/today
   ```

2. **Ver eventos sincronizados:**
   ```bash
   GET /api/v1/calendar/events
   ```

3. **Actualizar metadata local:**
   ```bash
   PATCH /api/v1/calendar/events/{id}
   # Agregar categoría/prioridad a evento de Google
   ```

---

## Integración con Python

```python
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1/calendar"

# Crear evento
def create_event():
    event = {
        "google_event_id": "python_event_001",
        "summary": "Llamada con equipo",
        "start_datetime": datetime.now().isoformat(),
        "end_datetime": (datetime.now() + timedelta(hours=1)).isoformat(),
        "category": "TRABAJO",
        "priority": "high"
    }
    response = requests.post(f"{BASE_URL}/events", json=event)
    return response.json()

# Listar eventos de TRABAJO
def list_work_events():
    response = requests.get(f"{BASE_URL}/events", params={"category": "TRABAJO"})
    return response.json()

# Buscar eventos por texto
def search_events(query):
    response = requests.get(f"{BASE_URL}/events", params={"search": query})
    return response.json()

# Filtrar por rango de fechas
def events_in_range(start_date, end_date):
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }
    response = requests.get(f"{BASE_URL}/events", params=params)
    return response.json()

# Actualizar prioridad
def update_priority(event_id, new_priority):
    response = requests.patch(
        f"{BASE_URL}/events/{event_id}",
        json={"priority": new_priority}
    )
    return response.json()

# Uso
event = create_event()
print(f"Evento creado: {event['id']}")

# Listar eventos de trabajo
events = list_work_events()
print(f"Eventos de trabajo: {len(events)}")

# Buscar eventos
gym_events = search_events("gym")
print(f"Eventos con 'gym': {len(gym_events)}")

# Eventos de esta semana
from datetime import datetime, timedelta
today = datetime.now()
week_end = today + timedelta(days=7)
week_events = events_in_range(today, week_end)
print(f"Eventos esta semana: {len(week_events)}")

# Actualizar prioridad
updated = update_priority(event['id'], 'critical')
print(f"Prioridad actualizada: {updated['priority']}")
```

---

## Swagger UI

Accede a la documentación interactiva en:
```
http://localhost:8000/docs
```

Desde ahí puedes probar todos los endpoints directamente desde el navegador.

---

## Próximas Funcionalidades

- [ ] Sincronización bidireccional (crear eventos en Google Calendar)
- [x] Búsqueda por texto en título/descripción ✅ **IMPLEMENTADO**
- [x] Filtros por rango de fechas ✅ **IMPLEMENTADO**
- [ ] Notificaciones de eventos próximos
- [ ] Exportar eventos a formatos (iCal, JSON, CSV)
