# 🚀 Mnemos v1.1 - Nuevas Características

## ✨ Resumen de Cambios

Se han implementado 3 características principales:

### 1. 🔄 Sincronización Bidireccional con Google Calendar
Ahora puedes crear, actualizar y eliminar eventos en Google Calendar directamente desde Mnemos.

### 2. 📊 Sistema de Analytics y Estadísticas
Nuevos endpoints para analizar el uso del tiempo con métricas de productividad.

### 3. 📈 Dashboard de Streamlit
Visualización interactiva de estadísticas con gráficos y métricas en tiempo real.

### 4. 🔭 OpenTelemetry Integration
Logging, tracing y metrics con estándar de observabilidad moderno.

---

## 🔄 1. Sincronización Bidireccional

### Nuevos Endpoints

#### Crear/Actualizar Evento en Google Calendar
```bash
POST /api/v1/calendar/events/{event_id}/push
```

**Comportamiento:**
- Si el evento es local (`google_event_id` comienza con "local_"): **crea** en Google Calendar
- Si ya existe en Google Calendar: **actualiza** el evento

**Ejemplo:**
```bash
# Crear evento local primero
curl -X POST http://localhost:8000/api/v1/calendar/events \
  -H "Content-Type: application/json" \
  -d '{
    "google_event_id": "local_meeting_001",
    "summary": "Reunión importante",
    "start_datetime": "2026-02-22T10:00:00",
    "end_datetime": "2026-02-22T11:00:00",
    "category": "TRABAJO",
    "priority": "high"
  }'

# Ahora pushear a Google Calendar
curl -X POST http://localhost:8000/api/v1/calendar/events/1/push
```

**Respuesta:**
```json
{
  "id": 1,
  "google_event_id": "abc123xyz",  // ← Ahora tiene ID de Google
  "summary": "Reunión importante",
  ...
}
```

---

#### Eliminar Evento de Google Calendar
```bash
DELETE /api/v1/calendar/events/{event_id}/sync
```

**Comportamiento:**
- Elimina el evento de Google Calendar (si existe)
- Elimina el evento de la base de datos local

**Ejemplo:**
```bash
curl -X DELETE http://localhost:8000/api/v1/calendar/events/1/sync
```

**Respuesta:**
```json
{
  "message": "Event 1 deleted from both local database and Google Calendar",
  "google_event_id": "abc123xyz"
}
```

---

### ⚠️ Importante: Actualizar Credenciales

Las credenciales de Google Calendar ahora necesitan permisos de **lectura y escritura**:

**Antes:**
```python
scopes=["https://www.googleapis.com/auth/calendar.readonly"]
```

**Ahora:**
```python
scopes=["https://www.googleapis.com/auth/calendar"]  # Read & Write
```

**Cómo actualizar:**
1. Ve a Google Cloud Console
2. Regenera las credenciales de Service Account
3. Descarga el nuevo archivo JSON
4. Reemplaza `credentials/service-account.json`
5. Reinicia el servidor

---

## 📊 2. Sistema de Analytics

### Nuevos Endpoints

#### Métricas Generales

```bash
GET /api/v1/analytics/time-by-category
GET /api/v1/analytics/time-by-priority
GET /api/v1/analytics/productivity-metrics
GET /api/v1/analytics/category-breakdown
```

**Query Parameters (opcionales):**
- `start_date`: Fecha de inicio (ISO 8601)
- `end_date`: Fecha de fin (ISO 8601)

**Ejemplo:**
```bash
# Métricas de productividad del último mes
curl "http://localhost:8000/api/v1/analytics/productivity-metrics?start_date=2026-01-20T00:00:00&end_date=2026-02-20T23:59:59"
```

**Respuesta:**
```json
{
  "total_hours": 120.5,
  "trabajo_hours": 80.0,
  "trabajo_percentage": 66.4,
  "salud_hours": 25.0,
  "salud_percentage": 20.7,
  "ocio_hours": 15.5,
  "ocio_percentage": 12.9,
  "high_priority_hours": 60.0,
  "high_priority_percentage": 49.8
}
```

---

#### Resúmenes Temporales

```bash
GET /api/v1/analytics/daily-summary
GET /api/v1/analytics/weekly-summary
GET /api/v1/analytics/this-week
GET /api/v1/analytics/this-month
```

**Ejemplo - Estadísticas de esta semana:**
```bash
curl http://localhost:8000/api/v1/analytics/this-week
```

**Respuesta:**
```json
{
  "period": {
    "start": "2026-02-17T00:00:00",
    "end": "2026-02-23T23:59:59"
  },
  "time_by_category": {
    "TRABAJO": 32.5,
    "SALUD": 8.0,
    "OCIO": 5.5
  },
  "time_by_priority": {
    "high": 20.0,
    "medium": 15.0,
    "low": 11.0
  },
  "productivity_metrics": { ... },
  "daily_summary": [ ... ]
}
```

---

#### Tendencias

```bash
GET /api/v1/analytics/trends?days=30
```

Compara los últimos N días con los N días anteriores.

**Ejemplo:**
```bash
curl "http://localhost:8000/api/v1/analytics/trends?days=30"
```

**Respuesta:**
```json
{
  "period_days": 30,
  "total_hours": {
    "value": 120.5,
    "change": 15.2,
    "change_percentage": 14.4
  },
  "trabajo_hours": {
    "value": 80.0,
    "change": -5.0,
    "change_percentage": -5.9
  }
}
```

---

## 📈 3. Dashboard de Streamlit

### Instalación

```bash
# Las dependencias ya están en pyproject.toml
uv sync

# O si usas pip
pip install streamlit plotly pandas
```

### Ejecutar Dashboard

```bash
# Terminal 1: Servidor FastAPI
uv run uvicorn main:app --reload

# Terminal 2: Dashboard Streamlit
uv run streamlit run streamlit_app.py
```

El dashboard se abrirá automáticamente en: `http://localhost:8501`

---

### Características del Dashboard

#### 📊 KPIs Principales
- Horas totales
- Horas por categoría (TRABAJO, SALUD, OCIO)
- Porcentajes de distribución

#### 📈 Gráficos Interactivos
- **Pie Chart**: Distribución de tiempo por categoría
- **Bar Chart**: Tiempo por prioridad
- **Line Chart**: Evolución diaria de horas

#### 🔍 Análisis Detallado
- Desglose por categoría (horas, eventos, promedios, %)
- Tendencias comparativas
- Resumen diario en tabla

#### ⚙️ Filtros
- Esta semana
- Este mes
- Últimos 30/90 días
- Período personalizado (selector de fechas)

---

### Screenshots (Descripción)

**Vista Principal:**
```
┌─────────────────────────────────────────────────┐
│  Mnemos Analytics Dashboard                     │
│  ════════════════════════════════════════════   │
│                                                  │
│  ⏱️ 120.5h  💼 80.0h  💪 25.0h  🎮 15.5h      │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐           │
│  │ Pie Chart    │  │ Bar Chart    │           │
│  │ Por Categoría│  │ Por Prioridad│           │
│  └──────────────┘  └──────────────┘           │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                                  │
│  📅 Resumen Diario                              │
│  ▂▃▅▇▆▄▃▂ (Line chart)                        │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## 🔭 4. OpenTelemetry Integration

### Configuración

Actualiza tu `.env`:

```bash
# Habilitar OpenTelemetry
OTEL_ENABLED=true

# Nombre del servicio
OTEL_SERVICE_NAME=mnemos

# Endpoint OTLP (opcional)
# OTEL_EXPORTER_ENDPOINT=http://localhost:4317

# Ambiente
OTEL_ENVIRONMENT=development
```

---

### Modos de Operación

#### Modo Console (Desarrollo)
```bash
OTEL_ENABLED=true
# No configurar OTEL_EXPORTER_ENDPOINT
```

Los traces, metrics y logs se mostrarán en la consola.

#### Modo OTLP (Producción)
```bash
OTEL_ENABLED=true
OTEL_EXPORTER_ENDPOINT=http://localhost:4317
```

Envía datos a un colector OTLP (Jaeger, Honeycomb, Datadog, etc.)

---

### Herramientas Compatibles

#### Jaeger (Local)
```bash
# Docker Compose
docker run -d --name jaeger \
  -p 16686:16686 \
  -p 4317:4317 \
  jaegertracing/all-in-one:latest

# Configurar
OTEL_EXPORTER_ENDPOINT=http://localhost:4317

# Ver traces en
http://localhost:16686
```

#### Honeycomb
```bash
OTEL_EXPORTER_ENDPOINT=https://api.honeycomb.io:443
OTEL_HONEYCOMB_API_KEY=your_api_key
```

#### Datadog
```bash
OTEL_EXPORTER_ENDPOINT=http://localhost:4318
# Requiere Datadog Agent
```

---

### Métricas Personalizadas

Se registran automáticamente:

- `mnemos.events.synced` - Eventos sincronizados
- `mnemos.events.created` - Eventos creados
- `mnemos.events.updated` - Eventos actualizados
- `mnemos.events.deleted` - Eventos eliminados
- `mnemos.events.duration` - Duración de eventos (histogram)
- `mnemos.sync.duration` - Tiempo de sincronización (histogram)

---

## 📦 Instalación Completa

### 1. Actualizar Dependencias

```bash
# Con uv (recomendado)
uv sync

# O con pip
pip install -r requirements.txt
```

### 2. Actualizar Variables de Entorno

```bash
cp .env.example .env.new
# Copiar tus valores actuales + nuevas variables
# Renombrar .env.new a .env
```

### 3. Actualizar Credenciales de Google

Si quieres usar sincronización bidireccional, regenera las credenciales con permisos de escritura.

### 4. Ejecutar Servicios

```bash
# API
uv run uvicorn main:app --reload

# Dashboard (terminal separado)
uv run streamlit run streamlit_app.py

# OpenTelemetry (opcional)
docker run -d -p 4317:4317 -p 16686:16686 jaegertracing/all-in-one:latest
```

---

## 🧪 Testing

### Sincronización Bidireccional

```bash
# 1. Crear evento local
curl -X POST http://localhost:8000/api/v1/calendar/events \
  -H "Content-Type: application/json" \
  -d '{
    "google_event_id": "local_test_001",
    "summary": "Test Event",
    "start_datetime": "2026-02-22T14:00:00",
    "end_datetime": "2026-02-22T15:00:00"
  }'

# 2. Push a Google Calendar
curl -X POST http://localhost:8000/api/v1/calendar/events/1/push

# 3. Verificar en Google Calendar web
# El evento debería aparecer

# 4. Eliminar sincronizado
curl -X DELETE http://localhost:8000/api/v1/calendar/events/1/sync

# 5. Verificar eliminación en Google Calendar
```

### Analytics

```bash
# Estadísticas de esta semana
curl http://localhost:8000/api/v1/analytics/this-week | jq

# Productividad del mes
curl http://localhost:8000/api/v1/analytics/this-month | jq

# Tendencias
curl "http://localhost:8000/api/v1/analytics/trends?days=30" | jq
```

### Dashboard

```bash
# 1. Iniciar servidor
uv run uvicorn main:app --reload

# 2. Sincronizar algunos eventos
curl -X POST http://localhost:8000/api/v1/calendar/sync/month

# 3. Iniciar dashboard
uv run streamlit run streamlit_app.py

# 4. Abrir en navegador
# http://localhost:8501
```

---

## 📝 Actualización de Documentación

La documentación técnica (`docs/TECHNICAL_DOCUMENTATION.md`) ha sido actualizada con:

- Nuevos endpoints de sincronización bidireccional
- Sistema de analytics completo
- Configuración de OpenTelemetry
- Guía de uso de Streamlit

---

## 🐛 Troubleshooting

### Error: "Calendar API permission denied"
**Solución:** Regenera credenciales con scope `calendar` (no `calendar.readonly`)

### Dashboard no se conecta a la API
**Solución:** Verifica que `API_BASE_URL` en `.env` apunte al servidor correcto

### OpenTelemetry no exporta datos
**Solución:** Verifica que `OTEL_EXPORTER_ENDPOINT` sea correcto y el colector esté running

### Streamlit muestra error de imports
**Solución:** `uv sync` o `pip install streamlit plotly pandas`

---

## 🎯 Próximos Pasos (Sugeridos)

1. **Tests Automatizados** - Pytest para endpoints de analytics y sync
2. **Docker Compose** - Stack completo (API + Streamlit + Jaeger)
3. **Webhooks de Google Calendar** - Sincronización automática en tiempo real
4. **Notificaciones** - Alertas por email/Telegram de eventos próximos
5. **Exportación** - iCal, CSV, PDF de reportes

---

¿Alguna duda o problema? Revisa la documentación completa en `docs/TECHNICAL_DOCUMENTATION.md`
