# Integración Mnemos ↔ Janus

Esta guía documenta cómo Janus debe consumir los endpoints de Mnemos para obtener eventos priorizados y filtrados.

---

## 📋 Configuración Requerida en Mnemos

En el archivo `.env` de Mnemos, configurar las variables de priorización:

```env
# Categorías consideradas de alta prioridad
HIGH_PRIORITY_CATEGORIES=TRABAJO

# Niveles de prioridad considerados altos
HIGH_PRIORITY_LEVELS=critical,high

# Categoría para eventos de rutina
ROUTINE_CATEGORY=RUTINA
```

**Valores por defecto si no están configuradas:**
- `HIGH_PRIORITY_CATEGORIES = ["TRABAJO"]`
- `HIGH_PRIORITY_LEVELS = ["critical", "high"]`
- `ROUTINE_CATEGORY = "RUTINA"`

---

## 🎯 Endpoint Principal para Janus

```
GET /api/v1/calendar/events
```

### Parámetros Clave

| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `date` | string | Fecha relativa o absoluta | `today`, `tomorrow`, `2026-02-25` |
| `prioritized` | boolean | Retornar eventos agrupados | `true` |
| `category` | string | Filtrar por categoría (case-insensitive) | `TRABAJO`, `trabajo` |

---

## 📊 Casos de Uso para Janus

### 1️⃣ Obtener eventos de hoy priorizados

**Request:**
```bash
GET /api/v1/calendar/events?date=today&prioritized=true
```

**Response:**
```json
{
  "high_priority": [
    {
      "id": 1,
      "summary": "Reunión cliente",
      "description": "Presentación Q1",
      "category": "TRABAJO",
      "priority": "critical",
      "start_datetime": "2026-02-20T10:00:00",
      "end_datetime": "2026-02-20T11:30:00"
    }
  ],
  "regular": [
    {
      "id": 3,
      "summary": "Gym",
      "category": "SALUD",
      "priority": "medium",
      "start_datetime": "2026-02-20T18:00:00",
      "end_datetime": "2026-02-20T19:00:00"
    }
  ],
  "routines": [
    {
      "id": 5,
      "summary": "Desayuno",
      "category": "RUTINA",
      "start_datetime": "2026-02-20T07:00:00",
      "end_datetime": "2026-02-20T07:30:00"
    }
  ],
  "counts": {
    "high_priority": 1,
    "regular": 1,
    "routines": 1,
    "total": 3,
    "by_category": {
      "TRABAJO": 1,
      "SALUD": 1,
      "RUTINA": 1
    }
  },
  "config": {
    "high_priority_categories": ["TRABAJO"],
    "high_priority_levels": ["critical", "high"],
    "routine_category": "RUTINA"
  }
}
```

**Uso en Janus:**
```python
import requests

response = requests.get(
    "http://mnemos-api/api/v1/calendar/events",
    params={
        "date": "today",
        "prioritized": True
    }
)
data = response.json()

# Acceder a eventos de alta prioridad
high_priority_events = data["high_priority"]
print(f"Tienes {len(high_priority_events)} eventos importantes hoy")

# Acceder a contadores
total = data["counts"]["total"]
high = data["counts"]["high_priority"]
print(f"Total: {total} eventos | Alta prioridad: {high}")
```

---

### 2️⃣ Obtener solo rutinas de hoy

**Request:**
```bash
GET /api/v1/calendar/events?date=today&category=RUTINA
```

**Response (Array plano - backward compatible):**
```json
[
  {
    "id": 5,
    "summary": "Desayuno",
    "category": "RUTINA",
    "start_datetime": "2026-02-20T07:00:00",
    "end_datetime": "2026-02-20T07:30:00"
  },
  {
    "id": 6,
    "summary": "Commute trabajo",
    "category": "RUTINA",
    "start_datetime": "2026-02-20T08:00:00",
    "end_datetime": "2026-02-20T08:30:00"
  }
]
```

**Uso en Janus:**
```python
response = requests.get(
    "http://mnemos-api/api/v1/calendar/events",
    params={
        "date": "today",
        "category": "RUTINA"
    }
)
routines = response.json()
print(f"Tienes {len(routines)} rutinas hoy")
```

---

### 3️⃣ Solo eventos de TRABAJO de hoy, priorizados

**Request:**
```bash
GET /api/v1/calendar/events?date=today&category=TRABAJO&prioritized=true
```

**Response:**
```json
{
  "high_priority": [
    {
      "id": 1,
      "summary": "Reunión cliente",
      "priority": "critical",
      "category": "TRABAJO"
    },
    {
      "id": 2,
      "summary": "Code review",
      "priority": "high",
      "category": "TRABAJO"
    }
  ],
  "regular": [
    {
      "id": 4,
      "summary": "Planning semanal",
      "priority": "medium",
      "category": "TRABAJO"
    }
  ],
  "routines": [],
  "counts": {
    "high_priority": 2,
    "regular": 1,
    "routines": 0,
    "total": 3,
    "by_category": {
      "TRABAJO": 3
    }
  }
}
```

---

### 4️⃣ Eventos de mañana

**Request:**
```bash
GET /api/v1/calendar/events?date=tomorrow
```

**Response (Array plano):**
```json
[
  {
    "id": 10,
    "summary": "Dentista",
    "category": "SALUD",
    "start_datetime": "2026-02-21T09:00:00"
  }
]
```

---

## 🎨 Formato de Mensajes para Telegram

### Ejemplo: Comando `/hoy` en Janus

```python
def format_today_events(data):
    """Formatea eventos de hoy para Telegram."""
    
    high = data["high_priority"]
    regular = data["regular"]
    routines = data["routines"]
    counts = data["counts"]
    
    message = f"📅 *Eventos de Hoy* ({counts['total']} total)\n\n"
    
    # Alta prioridad
    if high:
        message += "🔴 *Alta Prioridad* ({}):\n".format(len(high))
        for event in high:
            time = event["start_datetime"][:5]  # HH:MM
            message += f"  • {time} - {event['summary']}\n"
        message += "\n"
    
    # Regulares
    if regular:
        message += "🔵 *Regular* ({}):\n".format(len(regular))
        for event in regular:
            time = event["start_datetime"][:5]
            message += f"  • {time} - {event['summary']}\n"
        message += "\n"
    
    # Rutinas (colapsadas)
    if routines:
        message += f"⚪ *Rutinas* ({len(routines)}) - /ver_rutinas para detalles\n"
    
    return message

# Uso
response = requests.get(
    "http://mnemos-api/api/v1/calendar/events",
    params={"date": "today", "prioritized": True}
)
data = response.json()
telegram_message = format_today_events(data)
```

**Salida en Telegram:**
```
📅 Eventos de Hoy (5 total)

🔴 Alta Prioridad (2):
  • 10:00 - Reunión cliente
  • 14:00 - Code review

🔵 Regular (2):
  • 12:00 - Planning semanal
  • 18:00 - Gym

⚪ Rutinas (9) - /ver_rutinas para detalles
```

---

## ⚠️ Manejo de Errores

### Fecha inválida

**Request:**
```bash
GET /api/v1/calendar/events?date=invalid
```

**Response (400 Bad Request):**
```json
{
  "detail": "Invalid date format. Use 'today', 'tomorrow', or 'YYYY-MM-DD'"
}
```

**Manejo en Janus:**
```python
try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400:
        return "⚠️ Formato de fecha inválido. Usa 'hoy', 'mañana', o 'YYYY-MM-DD'"
```

### Sin eventos

**Response (200 OK):**
```json
{
  "high_priority": [],
  "regular": [],
  "routines": [],
  "counts": {
    "high_priority": 0,
    "regular": 0,
    "routines": 0,
    "total": 0,
    "by_category": {}
  },
  "config": {...}
}
```

**Manejo en Janus:**
```python
if data["counts"]["total"] == 0:
    return "✅ No tienes eventos hoy. ¡Día libre!"
```

---

## 🔄 Flujo Completo en Janus

### Comando `/hoy`

1. **Request a Mnemos:**
   ```python
   GET /api/v1/calendar/events?date=today&prioritized=true
   ```

2. **Procesar respuesta:**
   ```python
   data = response.json()
   high_priority = data["high_priority"]
   regular = data["regular"]
   routines = data["routines"]
   ```

3. **Formatear para Telegram:**
   ```python
   message = format_events(high_priority, regular, routines)
   ```

4. **Enviar a usuario:**
   ```python
   bot.send_message(chat_id, message, parse_mode="Markdown")
   ```

### Comando `/semana`

```python
# Similar a /hoy, pero obtener eventos de un rango
GET /api/v1/calendar/events?start_date=2026-02-20T00:00:00&end_date=2026-02-27T23:59:59&prioritized=true
```

### Comando `/rutinas`

```python
GET /api/v1/calendar/events?date=today&category=RUTINA
```

---

## 📚 Resumen de Endpoints para Janus

| Comando Janus | Request Mnemos | Uso |
|---------------|----------------|-----|
| `/hoy` | `GET /events?date=today&prioritized=true` | Eventos de hoy agrupados |
| `/manana` | `GET /events?date=tomorrow&prioritized=true` | Eventos de mañana |
| `/semana` | `GET /events?start_date=X&end_date=Y` | Eventos de la semana |
| `/rutinas` | `GET /events?date=today&category=RUTINA` | Solo rutinas de hoy |
| `/trabajo` | `GET /events?date=today&category=TRABAJO` | Solo eventos de trabajo |

---

## ✅ Checklist de Validación

Al consumir el API de Mnemos desde Janus, asegúrate de:

- [x] Usar `?prioritized=true` para obtener eventos agrupados
- [x] Usar `?date=today` en lugar de calcular start_date/end_date manualmente
- [x] Filtro por categoría es case-insensitive (`TRABAJO` = `trabajo`)
- [x] Manejar respuesta con estructura `{high_priority, regular, routines, counts, config}`
- [x] Usar `counts.total` para validar si hay eventos
- [x] Manejar errores 400 (fecha inválida)
- [x] Colapsar rutinas en la UI (mostrar solo contador)
- [x] Respetar configuración en `data["config"]` (es dinámica)

---

## 🚀 Próximos Pasos

Una vez que Janus esté consumiendo estos endpoints correctamente:

1. Implementar comandos de Telegram (`/hoy`, `/semana`, `/rutinas`)
2. Formatear mensajes para Telegram con Markdown
3. Agregar persistencia para guardar contexto de conversación
4. Implementar notificaciones proactivas
