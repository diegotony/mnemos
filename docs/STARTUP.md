# 🚀 Guía de Inicio - mnemos

## Inicio Rápido

### Opción 1: Ambos Servicios (Recomendado)

```bash
uv run start.py
```

Este script Python inicia automáticamente:
- **FastAPI** en `http://localhost:8000` (API REST)
- **Streamlit** en `http://localhost:8501` (Dashboard)

**Características:**
- ✅ Manejo automático de señales (Ctrl+C)
- ✅ Logs en `/tmp/mnemos_fastapi.log` y `/tmp/mnemos_streamlit.log`
- ✅ Monitoreo de procesos (reinicia si alguno falla)
- ✅ Shutdown limpio de ambos servicios

---

## Opciones Alternativas

### Opción 2: Scripts de `pyproject.toml`

**Solo API:**
```bash
uv run start-api
# Equivalente a: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Solo UI:**
```bash
uv run start-ui
# Equivalente a: streamlit run streamlit_app.py --server.port 8501
```

### Opción 3: Bash Script (Legacy)

```bash
./start.sh
```

Este script bash hace lo mismo que `start.py` pero usa sintaxis shell.

### Opción 4: Manual

**Terminal 1 - FastAPI:**
```bash
uv run uvicorn main:app --reload
```

**Terminal 2 - Streamlit:**
```bash
uv run streamlit run streamlit_app.py
```

---

## Verificación

Una vez iniciados los servicios, verifica que estén funcionando:

```bash
# Verificar FastAPI
curl http://localhost:8000/health

# Verificar Streamlit (abre en navegador)
open http://localhost:8501
```

---

## Logs y Debugging

**Ver logs en tiempo real:**
```bash
# FastAPI
tail -f /tmp/mnemos_fastapi.log

# Streamlit
tail -f /tmp/mnemos_streamlit.log
```

**Limpiar logs antiguos:**
```bash
rm /tmp/mnemos_*.log
```

---

## Variables de Entorno

El script `start.py` respeta el archivo `.env` en la raíz del proyecto.

**Importante para Streamlit:**
```env
API_BASE_URL=http://localhost:8000/api/v1
```

Ver [DATABASE_SETUP.md](DATABASE_SETUP.md) y `.env.example` para más configuraciones.

---

## Troubleshooting

### Puerto ya en uso

**Error:** `Address already in use`

**Solución:**
```bash
# Encuentra el proceso usando el puerto
lsof -i :8000  # FastAPI
lsof -i :8501  # Streamlit

# Mata el proceso
kill -9 <PID>
```

### Streamlit no puede conectarse a la API

1. Verifica que FastAPI esté corriendo: `curl http://localhost:8000/health`
2. Revisa `API_BASE_URL` en tu `.env`
3. Chequea los logs: `tail -f /tmp/mnemos_fastapi.log`

### Google Calendar no sincroniza

1. Verifica que exista `credentials/service-account.json`
2. Confirma las variables en `.env`:
   - `GOOGLE_SERVICE_ACCOUNT_FILE`
   - `GOOGLE_CALENDAR_ID`
   - `TIMEZONE`

Ver [CALENDAR_API_USAGE.md](CALENDAR_API_USAGE.md) para más detalles.

---

## Arquitectura del Sistema de Inicio

```
start.py (Python)
    │
    ├─► ServiceManager
    │       │
    │       ├─► start_service("FastAPI", ...)
    │       │       └─► subprocess.Popen(uvicorn)
    │       │
    │       └─► start_service("Streamlit", ...)
    │               └─► subprocess.Popen(streamlit)
    │
    └─► signal_handler(SIGINT/SIGTERM)
            └─► stop_all() → Terminate both processes
```

**Ventajas sobre `start.sh`:**
- ✅ Multiplataforma (funciona en Windows/Linux/macOS)
- ✅ Mejor manejo de errores
- ✅ Integrado con el entorno de `uv`
- ✅ Más fácil de extender (agregar más servicios)

---

## Próximos Pasos

Una vez que los servicios estén corriendo:

1. **Accede al Dashboard**: http://localhost:8501
2. **Explora la API**: http://localhost:8000/docs
3. **Lee la documentación**:
   - [CALENDAR_API_USAGE.md](CALENDAR_API_USAGE.md) - Uso de Google Calendar
   - [DATABASE_SETUP.md](DATABASE_SETUP.md) - Configuración de BD
   - [README.md](../README.md) - Información general

---

**mnemos** - Gestiona tu tiempo de forma simple y efectiva
