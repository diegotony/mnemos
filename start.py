#!/usr/bin/env python3
"""
Script para iniciar FastAPI y Streamlit simultáneamente.
Uso: uv run start.py
"""

import signal
import subprocess
import sys
import time
from pathlib import Path


class ServiceManager:
    """Gestor de servicios para FastAPI y Streamlit."""

    def __init__(self):
        self.processes = []
        self.running = True

    def signal_handler(self, signum, frame):
        """Maneja señales de interrupción (Ctrl+C)."""
        print("\n🛑 Deteniendo servicios...")
        self.running = False
        self.stop_all()
        sys.exit(0)

    def start_service(
        self, name: str, command: list[str], log_file: str
    ) -> subprocess.Popen:
        """Inicia un servicio y registra su proceso."""
        print(f"🚀 Iniciando {name}...")

        log_path = Path(log_file)
        with open(log_path, "w") as log:
            process = subprocess.Popen(
                command, stdout=log, stderr=subprocess.STDOUT, text=True
            )

        self.processes.append({"name": name, "process": process, "log": log_file})
        print(f"   ├─ PID: {process.pid}")
        print(f"   └─ Log: {log_file}")
        return process

    def stop_all(self):
        """Detiene todos los servicios activos."""
        for service in self.processes:
            try:
                service["process"].terminate()
                service["process"].wait(timeout=5)
                print(f"✅ {service['name']} detenido")
            except subprocess.TimeoutExpired:
                service["process"].kill()
                print(f"⚠️  {service['name']} forzado a detenerse")
            except Exception as e:
                print(f"❌ Error deteniendo {service['name']}: {e}")

    def run(self):
        """Ejecuta ambos servicios."""
        # Registrar manejador de señales
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Iniciar FastAPI
        fastapi_cmd = [
            "uvicorn",
            "main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
            "--reload",
        ]
        self.start_service("FastAPI", fastapi_cmd, "/tmp/mnemos_fastapi.log")

        # Pequeña pausa para que FastAPI inicie primero
        time.sleep(1)

        # Iniciar Streamlit
        streamlit_cmd = [
            "streamlit",
            "run",
            "streamlit_app.py",
            "--server.port",
            "8501",
            "--server.headless",
            "true",
        ]
        self.start_service("Streamlit", streamlit_cmd, "/tmp/mnemos_streamlit.log")

        print("\n" + "=" * 60)
        print("✨ Servicios iniciados correctamente")
        print("=" * 60)
        print("📡 FastAPI:    http://localhost:8000")
        print("📊 Streamlit:  http://localhost:8501")
        print("📄 Docs:       http://localhost:8000/docs")
        print("=" * 60)
        print("💡 Presiona Ctrl+C para detener ambos servicios\n")

        # Monitorear procesos
        try:
            while self.running:
                for service in self.processes:
                    if service["process"].poll() is not None:
                        print(f"⚠️  {service['name']} se detuvo inesperadamente")
                        print(f"   Ver log: {service['log']}")
                        self.stop_all()
                        sys.exit(1)
                time.sleep(1)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    manager = ServiceManager()
    manager.run()
