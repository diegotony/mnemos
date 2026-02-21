# Campos Disponibles en Calendar Events

## Resumen de Schemas

### 📋 CalendarEventRead (Detalle Completo)
**Usado en:**
- `GET /api/v1/calendar/events` - Listar eventos
- `GET /api/v1/calendar/events/{id}` - Obtener evento específico
- `POST /api/v1/calendar/events` - Crear evento
- `PUT /api/v1/calendar/events/{id}` - Actualizar evento
- `PATCH /api/v1/calendar/events/{id}` - Actualizar parcialmente

**Campos incluidos:**
```json
{
  "id": 1,
  "google_event_id": "event_001",
  "user_id": null,
  
  "summary": "Título del evento",           // ✅ Incluido
  "description": "Descripción detallada",   // ✅ Incluido
  "location": "Sala de conferencias",       // ✅ Incluido
  
  "start_datetime": "2026-02-21T10:00:00",
  "end_datetime": "2026-02-21T11:00:00",
  "all_day": false,
  
  "status": "confirmed",
  "priority": "high",
  "category": "TRABAJO",
  
  "extra_data": {                           // ✅ Incluido
    "attendees": ["Juan", "María"],
    "notes": "Cualquier dato adicional"
  },
  
  "created_at": "2026-02-21T02:00:00",
  "updated_at": "2026-02-21T02:00:00",
  "synced_at": "2026-02-21T02:00:00"
}
```

### 📝 CalendarEventSummary (Resumen)
**Usado en:**
- `POST /api/v1/calendar/sync/today` - Sincronizar eventos
- `POST /api/v1/calendar/sync/week`
- `POST /api/v1/calendar/sync/month`
- `POST /api/v1/calendar/sync/critical`

**Campos incluidos:**
```json
{
  "id": 1,
  "google_event_id": "event_001",
  "summary": "Título del evento",
  "start_datetime": "2026-02-21T10:00:00",
  "end_datetime": "2026-02-21T11:00:00",
  "all_day": false,
  "priority": "high",
  "category": "TRABAJO"
}
```

**❌ NO incluye:**
- `description`
- `location`
- `extra_data`
- `created_at`, `updated_at`, `synced_at`

---

## Obtener Descripción Completa

### ✅ Opción 1: Listar todos con descripción
```bash
GET /api/v1/calendar/events
```

**Ejemplo con curl:**
```bash
curl http://localhost:8000/api/v1/calendar/events | jq
```

**Response:**
```json
[
  {
    "id": 1,
    "summary": "Reunión importante",
    "description": "Esta es la descripción completa del evento...",
    "location": "Oficina central",
    "start_datetime": "2026-02-21T10:00:00",
    "end_datetime": "2026-02-21T11:00:00",
    "category": "TRABAJO",
    "priority": "high",
    "extra_data": {
      "notes": "Notas adicionales"
    }
  }
]
```

### ✅ Opción 2: Obtener evento específico
```bash
GET /api/v1/calendar/events/{id}
```

**Ejemplo con curl:**
```bash
curl http://localhost:8000/api/v1/calendar/events/1 | jq '.description'
```

**Response:**
```json
{
  "id": 1,
  "summary": "Reunión importante",
  "description": "Esta es la descripción completa...",
  "location": "Oficina central",
  ...
}
```

### ✅ Opción 3: Filtrar y obtener descripciones
```bash
GET /api/v1/calendar/events?category=TRABAJO
```

**Ejemplo con curl:**
```bash
curl "http://localhost:8000/api/v1/calendar/events?category=TRABAJO" | jq '.[] | {summary, description}'
```

**Response:**
```json
[
  {
    "summary": "Reunión de equipo",
    "description": "Revisar avances del sprint"
  },
  {
    "summary": "Sprint Planning",
    "description": "AGENDA:\n1. Review\n2. Retrospectiva..."
  }
]
```

---

## Workflow: Sync + Detalles

Si sincronizas eventos de Google Calendar y quieres ver las descripciones:

### 1. Sincronizar eventos (solo resumen)
```bash
POST /api/v1/calendar/sync/today
```

Response:
```json
[
  {
    "id": 10,
    "summary": "Reunión con cliente",
    "start_datetime": "...",
    "category": "TRABAJO"
  }
]
```

### 2. Obtener detalles completos (con descripción)
```bash
GET /api/v1/calendar/events/10
```

Response:
```json
{
  "id": 10,
  "summary": "Reunión con cliente",
  "description": "Descripción completa del evento de Google Calendar",
  "location": "Café Central",
  "extra_data": {...}
}
```

### 3. O listar todos con descripciones
```bash
GET /api/v1/calendar/events?category=TRABAJO
```

---

## Crear Evento con Descripción Rica

### Ejemplo: Evento con Markdown en descripción
```bash
POST /api/v1/calendar/events
Content-Type: application/json

{
  "google_event_id": "meeting_2026_02_21",
  "summary": "Reunión Trimestral Q1",
  "description": "## Agenda\n\n1. Resultados Q4 2025\n2. Objetivos Q1 2026\n3. Presupuesto\n\n## Preparación\n\n- Revisar métricas\n- Preparar presentación\n\n## Participantes\n\n- Equipo directivo\n- Gerentes de área",
  "location": "Auditorio Principal",
  "start_datetime": "2026-02-21T09:00:00-05:00",
  "end_datetime": "2026-02-21T12:00:00-05:00",
  "category": "TRABAJO",
  "priority": "critical",
  "extra_data": {
    "requires_presentation": true,
    "estimated_attendees": 25,
    "recording": true
  }
}
```

### Ejemplo: Evento médico
```bash
POST /api/v1/calendar/events
Content-Type: application/json

{
  "google_event_id": "medical_checkup_001",
  "summary": "Chequeo médico anual",
  "description": "INSTRUCCIONES:\n- Ayuno de 8 horas\n- Traer resultados anteriores\n- Llegar 15 min antes\n\nEXÁMENES:\n- Análisis de sangre\n- Presión arterial\n- Electrocardiograma",
  "location": "Clínica San Pablo - Piso 3",
  "start_datetime": "2026-03-15T08:00:00-05:00",
  "end_datetime": "2026-03-15T09:30:00-05:00",
  "category": "SALUD",
  "priority": "high",
  "extra_data": {
    "doctor": "Dr. García",
    "insurance": "Pacífico",
    "copay": 50
  }
}
```

---

## Actualizar Descripción

### Actualizar solo la descripción
```bash
PATCH /api/v1/calendar/events/1
Content-Type: application/json

{
  "description": "Nueva descripción actualizada con más detalles"
}
```

### Actualizar descripción + otros campos
```bash
PUT /api/v1/calendar/events/1
Content-Type: application/json

{
  "summary": "Título actualizado",
  "description": "Descripción actualizada",
  "priority": "critical"
}
```

---

## Buscar por Contenido (Próximamente)

Actualmente puedes filtrar por:
- ✅ `category` (TRABAJO, SALUD, OCIO, RUTINA)
- ✅ `priority` (low, medium, high, critical)

**Próximas funcionalidades:**
- [ ] Búsqueda por texto en `summary`
- [ ] Búsqueda por texto en `description`
- [ ] Filtro por rango de fechas
- [ ] Ordenamiento personalizado

**Workaround actual:**
```bash
# Obtener todos y filtrar localmente
curl http://localhost:8000/api/v1/calendar/events | \
  jq '.[] | select(.description | contains("sprint"))'
```

---

## Integración con Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1/calendar"

def get_event_with_description(event_id: int):
    """Obtiene evento completo incluyendo descripción"""
    response = requests.get(f"{BASE_URL}/events/{event_id}")
    event = response.json()
    
    print(f"Título: {event['summary']}")
    print(f"Descripción:\n{event['description']}")
    print(f"Ubicación: {event['location']}")
    
    return event

def get_all_work_events_with_details():
    """Lista todos los eventos de trabajo con descripciones"""
    response = requests.get(
        f"{BASE_URL}/events",
        params={"category": "TRABAJO"}
    )
    events = response.json()
    
    for event in events:
        print(f"\n--- {event['summary']} ---")
        if event['description']:
            print(f"Descripción: {event['description'][:100]}...")
        print(f"Fecha: {event['start_datetime']}")
    
    return events

def create_event_with_rich_description():
    """Crea evento con descripción detallada"""
    event = {
        "google_event_id": "python_event_002",
        "summary": "Workshop de Python",
        "description": """
## Temario
1. FastAPI avanzado
2. SQLAlchemy ORM
3. Testing con pytest

## Requisitos
- Laptop con Python 3.11+
- IDE configurado
- Entorno virtual

## Materiales
- Slides: drive.google.com/...
- Código: github.com/...
        """.strip(),
        "location": "Sala de capacitación",
        "start_datetime": "2026-03-01T14:00:00-05:00",
        "end_datetime": "2026-03-01T18:00:00-05:00",
        "category": "TRABAJO",
        "priority": "medium",
        "extra_data": {
            "max_capacity": 20,
            "requires_registration": True
        }
    }
    
    response = requests.post(f"{BASE_URL}/events", json=event)
    return response.json()

# Uso
event = get_event_with_description(1)
work_events = get_all_work_events_with_details()
new_event = create_event_with_rich_description()
```

---

## Tips

### ✅ Usar description para:
- Agendas detalladas
- Instrucciones de preparación
- Notas importantes
- Links a recursos
- Información de contacto

### ✅ Usar extra_data para:
- Datos estructurados
- Metadata personalizada
- Integraciones con otros sistemas
- Campos adicionales específicos

### ✅ Usar location para:
- Direcciones físicas
- Salas de reunión
- URLs de videollamadas
- Nombres de lugares

---

## Swagger UI

La forma más fácil de explorar todos los campos disponibles:

1. Abre: `http://localhost:8000/docs`
2. Busca `GET /api/v1/calendar/events/{event_id}`
3. Click en "Try it out"
4. Ingresa un ID de evento
5. Click "Execute"
6. Ver respuesta completa con todos los campos

También puedes ver los schemas:
- Busca "Schemas" al final de la página Swagger
- Click en `CalendarEventRead` para ver todos los campos
- Click en `CalendarEventSummary` para ver el resumen
