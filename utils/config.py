"""
Módulo de configuración centralizada para Mnemos.
Gestiona variables de entorno con validación y valores por defecto.
"""

import os
from typing import List
from dotenv import load_dotenv
from utils.logger import logger

load_dotenv()


class PriorityConfig:
    """Configuración para priorización de eventos."""

    # Categorías válidas
    VALID_CATEGORIES = ["TRABAJO", "SALUD", "OCIO", "RUTINA"]

    # Niveles de prioridad válidos
    VALID_PRIORITY_LEVELS = ["critical", "high", "medium", "low"]

    # Valores por defecto
    DEFAULT_HIGH_PRIORITY_CATEGORIES = ["TRABAJO"]
    DEFAULT_HIGH_PRIORITY_LEVELS = ["critical", "high"]
    DEFAULT_ROUTINE_CATEGORY = "RUTINA"

    def __init__(self):
        self.high_priority_categories = self._load_high_priority_categories()
        self.high_priority_levels = self._load_high_priority_levels()
        self.routine_category = self._load_routine_category()

    def _load_high_priority_categories(self) -> List[str]:
        """Carga y valida HIGH_PRIORITY_CATEGORIES desde .env."""
        env_value = os.getenv("HIGH_PRIORITY_CATEGORIES", "")

        if not env_value.strip():
            logger.info(
                f"⚙️  HIGH_PRIORITY_CATEGORIES no configurada, usando default: {self.DEFAULT_HIGH_PRIORITY_CATEGORIES}"
            )
            return self.DEFAULT_HIGH_PRIORITY_CATEGORIES.copy()

        # Parsear y limpiar
        categories = [
            cat.strip().upper() for cat in env_value.split(",") if cat.strip()
        ]

        # Validar que todas sean válidas
        invalid_categories = [
            cat for cat in categories if cat not in self.VALID_CATEGORIES
        ]

        if invalid_categories:
            logger.error(
                f"❌ HIGH_PRIORITY_CATEGORIES contiene valores inválidos: {invalid_categories}"
            )
            logger.error(f"   Valores válidos: {self.VALID_CATEGORIES}")
            logger.warning(
                f"   Usando valores por defecto: {self.DEFAULT_HIGH_PRIORITY_CATEGORIES}"
            )
            return self.DEFAULT_HIGH_PRIORITY_CATEGORIES.copy()

        logger.info(f"✅ HIGH_PRIORITY_CATEGORIES: {categories}")
        return categories

    def _load_high_priority_levels(self) -> List[str]:
        """Carga y valida HIGH_PRIORITY_LEVELS desde .env."""
        env_value = os.getenv("HIGH_PRIORITY_LEVELS", "")

        if not env_value.strip():
            logger.info(
                f"⚙️  HIGH_PRIORITY_LEVELS no configurada, usando default: {self.DEFAULT_HIGH_PRIORITY_LEVELS}"
            )
            return self.DEFAULT_HIGH_PRIORITY_LEVELS.copy()

        # Parsear y limpiar
        levels = [
            level.strip().lower() for level in env_value.split(",") if level.strip()
        ]

        # Validar que todos sean válidos
        invalid_levels = [
            level for level in levels if level not in self.VALID_PRIORITY_LEVELS
        ]

        if invalid_levels:
            logger.error(
                f"❌ HIGH_PRIORITY_LEVELS contiene valores inválidos: {invalid_levels}"
            )
            logger.error(f"   Valores válidos: {self.VALID_PRIORITY_LEVELS}")
            logger.warning(
                f"   Usando valores por defecto: {self.DEFAULT_HIGH_PRIORITY_LEVELS}"
            )
            return self.DEFAULT_HIGH_PRIORITY_LEVELS.copy()

        logger.info(f"✅ HIGH_PRIORITY_LEVELS: {levels}")
        return levels

    def _load_routine_category(self) -> str:
        """Carga y valida ROUTINE_CATEGORY desde .env."""
        env_value = os.getenv("ROUTINE_CATEGORY", "").strip().upper()

        if not env_value:
            logger.info(
                f"⚙️  ROUTINE_CATEGORY no configurada, usando default: {self.DEFAULT_ROUTINE_CATEGORY}"
            )
            return self.DEFAULT_ROUTINE_CATEGORY

        # Validar que sea una categoría válida
        if env_value not in self.VALID_CATEGORIES:
            logger.error(f"❌ ROUTINE_CATEGORY '{env_value}' no es válida")
            logger.error(f"   Valores válidos: {self.VALID_CATEGORIES}")
            logger.warning(
                f"   Usando valor por defecto: {self.DEFAULT_ROUTINE_CATEGORY}"
            )
            return self.DEFAULT_ROUTINE_CATEGORY

        logger.info(f"✅ ROUTINE_CATEGORY: {env_value}")
        return env_value


# Singleton global
_priority_config_instance = None


def get_priority_config() -> PriorityConfig:
    """
    Obtiene la instancia global de PriorityConfig (singleton).
    Se inicializa una vez al importar el módulo.
    """
    global _priority_config_instance
    if _priority_config_instance is None:
        _priority_config_instance = PriorityConfig()
    return _priority_config_instance
