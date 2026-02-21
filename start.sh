#!/bin/bash

# Script para iniciar FastAPI y Streamlit simultáneamente
# Uso: ./start.sh

echo "🚀 Iniciando Mnemos..."
echo ""

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para limpiar procesos al salir
cleanup() {
    echo ""
    echo "🛑 Deteniendo servicios..."
    kill $FASTAPI_PID $STREAMLIT_PID 2>/dev/null
    wait $FASTAPI_PID $STREAMLIT_PID 2>/dev/null
    echo "✅ Servicios detenidos"
    exit 0
}

# Registrar cleanup al recibir señal de interrupción
trap cleanup SIGINT SIGTERM

# Iniciar FastAPI en background
echo -e "${BLUE}📡 Iniciando FastAPI en http://localhost:8000${NC}"
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload > /tmp/mnemos_fastapi.log 2>&1 &
FASTAPI_PID=$!

# Esperar a que FastAPI esté listo
sleep 2

# Iniciar Streamlit en background
echo -e "${GREEN}📊 Iniciando Streamlit en http://localhost:8501${NC}"
uv run streamlit run streamlit_app.py > /tmp/mnemos_streamlit.log 2>&1 &
STREAMLIT_PID=$!

echo ""
echo "✅ Servicios iniciados:"
echo "   - FastAPI:   http://localhost:8000"
echo "   - API Docs:  http://localhost:8000/docs"
echo "   - Streamlit: http://localhost:8501"
echo ""
echo "📝 Logs:"
echo "   - FastAPI:   tail -f /tmp/mnemos_fastapi.log"
echo "   - Streamlit: tail -f /tmp/mnemos_streamlit.log"
echo ""
echo "🛑 Presiona Ctrl+C para detener todos los servicios"
echo ""

# Esperar indefinidamente (hasta Ctrl+C)
wait
