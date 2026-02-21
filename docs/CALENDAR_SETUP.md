# Google Calendar - Configuración Rápida

## ¿Cómo saber si está configurado?

Accede a: `http://localhost:8000/api/v1/calendar/health`

### ✅ Respuesta cuando está configurado:
```json
{
  "configured": true,
  "message": "✅ Google Calendar service is properly configured and ready to use"
}
```

### ❌ Respuesta cuando falta configuración:
```json
{
  "configured": false,
  "message": "❌ Service account file not found...",
  "help": "See docs/GOOGLE_CALENDAR_INTEGRATION.md"
}
```

## Configuración en 3 pasos

### 1. Obtener credenciales de Google

1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Crea un proyecto o selecciona uno existente
3. Habilita **Google Calendar API**
4. Ve a **Credentials** → **Create Credentials** → **Service Account**
5. Descarga el archivo JSON de credenciales

### 2. Guardar credenciales

```bash
# Copiar archivo descargado
cp ~/Downloads/tu-proyecto-*.json credentials/service-account.json

# Verificar que existe
ls -la credentials/service-account.json
```

### 3. Compartir calendario

1. Abre [Google Calendar](https://calendar.google.com)
2. Ve a **Settings** → Tu calendario
3. En **Share with specific people**, agrega el email del Service Account
   - Lo encuentras en el archivo JSON: campo `client_email`
   - Ejemplo: `mnemos@proyecto.iam.gserviceaccount.com`
4. Dale permisos de **"See all event details"**

## Verificar configuración

```bash
# Iniciar servidor
uv run uvicorn main:app --reload

# En otro terminal, verificar estado
curl http://localhost:8000/api/v1/calendar/health | jq

# Si está configurado, probar sincronización
curl http://localhost:8000/api/v1/calendar/sync/today
```

## Variables de entorno (.env)

```bash
# Google Calendar
GOOGLE_SERVICE_ACCOUNT_FILE=credentials/service-account.json
GOOGLE_CALENDAR_ID=tu@email.com  # Tu email de Google Calendar
TIMEZONE=America/Lima
```

## Troubleshooting

### Error: "Service account file not found"
- Verifica que el archivo existe en `credentials/service-account.json`
- Verifica que `GOOGLE_SERVICE_ACCOUNT_FILE` en `.env` apunte al archivo correcto

### Error: "Failed to initialize Google Calendar service"
- Verifica que el archivo JSON es válido
- Verifica que la API de Google Calendar está habilitada
- Verifica que compartiste el calendario con el Service Account

### Sync devuelve 0 eventos
- Verifica que compartiste el calendario con el Service Account
- Verifica que el calendario tiene eventos en el rango de fechas
- Verifica que `GOOGLE_CALENDAR_ID` en `.env` es correcto

## Documentación completa

Ver: `docs/GOOGLE_CALENDAR_INTEGRATION.md`
