"""
Router para endpoints de Analytics y Estadísticas.
Proporciona métricas sobre uso del tiempo.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import pytz

from dependencies.database import get_db
from services.analytics import AnalyticsService
from utils.logger import logger
import os


router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    """Dependency para obtener el servicio de analytics."""
    timezone = os.getenv("TIMEZONE", "America/Lima")
    return AnalyticsService(db, timezone)


@router.get("/time-by-category")
def get_time_by_category(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Obtiene tiempo total (en horas) por categoría.

    - **start_date**: Fecha de inicio (ISO 8601, opcional)
    - **end_date**: Fecha de fin (ISO 8601, opcional)

    Retorna dict con categoría -> horas totales.
    """
    return analytics.get_time_by_category(start_date, end_date)


@router.get("/time-by-priority")
def get_time_by_priority(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Obtiene tiempo total (en horas) por prioridad.

    - **start_date**: Fecha de inicio (ISO 8601, opcional)
    - **end_date**: Fecha de fin (ISO 8601, opcional)

    Retorna dict con prioridad -> horas totales.
    """
    return analytics.get_time_by_priority(start_date, end_date)


@router.get("/event-count-by-category")
def get_event_count_by_category(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Cuenta número de eventos por categoría.

    - **start_date**: Fecha de inicio (ISO 8601, opcional)
    - **end_date**: Fecha de fin (ISO 8601, opcional)

    Retorna dict con categoría -> número de eventos.
    """
    return analytics.get_event_count_by_category(start_date, end_date)


@router.get("/daily-summary")
def get_daily_summary(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Obtiene resumen diario de horas trabajadas.

    - **start_date**: Fecha de inicio (ISO 8601, opcional)
    - **end_date**: Fecha de fin (ISO 8601, opcional)

    Retorna lista de dicts con {date, total_hours, event_count}.
    """
    return analytics.get_daily_summary(start_date, end_date)


@router.get("/weekly-summary")
def get_weekly_summary(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Obtiene resumen semanal de horas trabajadas.

    - **start_date**: Fecha de inicio (ISO 8601, opcional)
    - **end_date**: Fecha de fin (ISO 8601, opcional)

    Retorna lista de dicts con {week, year, total_hours, event_count}.
    """
    return analytics.get_weekly_summary(start_date, end_date)


@router.get("/category-breakdown")
def get_category_breakdown(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Obtiene desglose completo por categoría.

    - **start_date**: Fecha de inicio (ISO 8601, opcional)
    - **end_date**: Fecha de fin (ISO 8601, opcional)

    Retorna dict con estadísticas por categoría:
    - total_hours
    - event_count
    - avg_hours_per_event
    - percentage_of_total
    """
    return analytics.get_category_breakdown(start_date, end_date)


@router.get("/productivity-metrics")
def get_productivity_metrics(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Calcula métricas de productividad.

    - **start_date**: Fecha de inicio (ISO 8601, opcional)
    - **end_date**: Fecha de fin (ISO 8601, opcional)

    Retorna métricas de productividad:
    - total_hours
    - trabajo_hours, trabajo_percentage
    - salud_hours, salud_percentage
    - ocio_hours, ocio_percentage
    - high_priority_hours, high_priority_percentage
    """
    return analytics.get_productivity_metrics(start_date, end_date)


@router.get("/trends")
def get_time_usage_trends(
    days: int = Query(30, ge=1, le=365, description="Días hacia atrás"),
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Analiza tendencias de uso del tiempo.

    - **days**: Número de días hacia atrás (default: 30, max: 365)

    Retorna tendencias comparando período actual vs período anterior:
    - total_hours (con cambio y porcentaje)
    - trabajo_hours (con cambio y porcentaje)
    - salud_hours (con cambio y porcentaje)
    - ocio_hours (con cambio y porcentaje)
    """
    return analytics.get_time_usage_trends(days)


@router.get("/this-week")
def get_this_week_stats(
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Obtiene estadísticas de la semana actual (lunes a domingo).

    Retorna métricas completas para la semana en curso.
    """
    timezone_str = os.getenv("TIMEZONE", "America/Lima")
    timezone = pytz.timezone(timezone_str)
    now = datetime.now(timezone)

    # Inicio de la semana (lunes)
    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    # Fin de la semana (domingo)
    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)

    return {
        "period": {"start": start_of_week.isoformat(), "end": end_of_week.isoformat()},
        "time_by_category": analytics.get_time_by_category(start_of_week, end_of_week),
        "time_by_priority": analytics.get_time_by_priority(start_of_week, end_of_week),
        "productivity_metrics": analytics.get_productivity_metrics(
            start_of_week, end_of_week
        ),
        "daily_summary": analytics.get_daily_summary(start_of_week, end_of_week),
    }


@router.get("/this-month")
def get_this_month_stats(
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Obtiene estadísticas del mes actual.

    Retorna métricas completas para el mes en curso.
    """
    timezone_str = os.getenv("TIMEZONE", "America/Lima")
    timezone = pytz.timezone(timezone_str)
    now = datetime.now(timezone)

    # Primer día del mes
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Último día del mes
    if now.month == 12:
        end_of_month = now.replace(
            year=now.year + 1,
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        ) - timedelta(seconds=1)
    else:
        end_of_month = now.replace(
            month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(seconds=1)

    return {
        "period": {
            "start": start_of_month.isoformat(),
            "end": end_of_month.isoformat(),
        },
        "time_by_category": analytics.get_time_by_category(
            start_of_month, end_of_month
        ),
        "time_by_priority": analytics.get_time_by_priority(
            start_of_month, end_of_month
        ),
        "productivity_metrics": analytics.get_productivity_metrics(
            start_of_month, end_of_month
        ),
        "category_breakdown": analytics.get_category_breakdown(
            start_of_month, end_of_month
        ),
        "weekly_summary": analytics.get_weekly_summary(start_of_month, end_of_month),
    }


# ========== IDEAS ANALYTICS ==========


@router.get("/ideas/total")
def get_ideas_total_count(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Cuenta el total de ideas creadas.

    - **start_date**: Fecha de inicio (ISO 8601, opcional)
    - **end_date**: Fecha de fin (ISO 8601, opcional)

    Retorna el número total de ideas.
    """
    return {"total_ideas": analytics.get_ideas_total_count(start_date, end_date)}


@router.get("/ideas/daily")
def get_ideas_daily_count(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Obtiene conteo diario de ideas creadas.

    - **start_date**: Fecha de inicio (ISO 8601, opcional)
    - **end_date**: Fecha de fin (ISO 8601, opcional)

    Retorna lista de dicts con {date, count}.
    """
    return analytics.get_ideas_daily_count(start_date, end_date)


@router.get("/ideas/weekly")
def get_ideas_weekly_count(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Obtiene conteo semanal de ideas creadas.

    - **start_date**: Fecha de inicio (ISO 8601, opcional)
    - **end_date**: Fecha de fin (ISO 8601, opcional)

    Retorna lista de dicts con {year, week, count}.
    """
    return analytics.get_ideas_weekly_count(start_date, end_date)


@router.get("/ideas/this-week")
def get_ideas_this_week(
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Obtiene estadísticas de ideas de la semana actual.

    Retorna conteo de ideas creadas esta semana.
    """
    timezone_str = os.getenv("TIMEZONE", "America/Lima")
    timezone = pytz.timezone(timezone_str)
    now = datetime.now(timezone)

    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)

    return {
        "period": {"start": start_of_week.isoformat(), "end": end_of_week.isoformat()},
        "total_ideas": analytics.get_ideas_total_count(start_of_week, end_of_week),
        "daily_breakdown": analytics.get_ideas_daily_count(start_of_week, end_of_week),
    }


@router.get("/ideas/this-month")
def get_ideas_this_month(
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Obtiene estadísticas de ideas del mes actual.

    Retorna conteo de ideas creadas este mes.
    """
    timezone_str = os.getenv("TIMEZONE", "America/Lima")
    timezone = pytz.timezone(timezone_str)
    now = datetime.now(timezone)

    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    if now.month == 12:
        end_of_month = now.replace(
            year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(seconds=1)
    else:
        end_of_month = now.replace(
            month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(seconds=1)

    return {
        "period": {
            "start": start_of_month.isoformat(),
            "end": end_of_month.isoformat(),
        },
        "total_ideas": analytics.get_ideas_total_count(start_of_month, end_of_month),
        "daily_breakdown": analytics.get_ideas_daily_count(
            start_of_month, end_of_month
        ),
        "weekly_breakdown": analytics.get_ideas_weekly_count(
            start_of_month, end_of_month
        ),
    }


# ========== INBOX ANALYTICS ==========


@router.get("/inbox/total")
def get_inbox_total_count(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Cuenta el total de inbox items.

    - **start_date**: Fecha de inicio (ISO 8601, opcional)
    - **end_date**: Fecha de fin (ISO 8601, opcional)

    Retorna el número total de inbox items.
    """
    return {"total_inbox": analytics.get_inbox_total_count(start_date, end_date)}


@router.get("/inbox/by-status")
def get_inbox_by_status(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Cuenta inbox items por status.

    - **start_date**: Fecha de inicio (ISO 8601, opcional)
    - **end_date**: Fecha de fin (ISO 8601, opcional)

    Retorna dict con status_id -> count.
    """
    return analytics.get_inbox_by_status(start_date, end_date)


@router.get("/inbox/by-source")
def get_inbox_by_source(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Cuenta inbox items por source.

    - **start_date**: Fecha de inicio (ISO 8601, opcional)
    - **end_date**: Fecha de fin (ISO 8601, opcional)

    Retorna dict con source -> count.
    """
    return analytics.get_inbox_by_source(start_date, end_date)


@router.get("/inbox/daily")
def get_inbox_daily_count(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Obtiene conteo diario de inbox items.

    - **start_date**: Fecha de inicio (ISO 8601, opcional)
    - **end_date**: Fecha de fin (ISO 8601, opcional)

    Retorna lista de dicts con {date, count}.
    """
    return analytics.get_inbox_daily_count(start_date, end_date)


@router.get("/inbox/weekly")
def get_inbox_weekly_count(
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin"),
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Obtiene conteo semanal de inbox items.

    - **start_date**: Fecha de inicio (ISO 8601, opcional)
    - **end_date**: Fecha de fin (ISO 8601, opcional)

    Retorna lista de dicts con {year, week, count}.
    """
    return analytics.get_inbox_weekly_count(start_date, end_date)


@router.get("/inbox/this-week")
def get_inbox_this_week(
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Obtiene estadísticas de inbox de la semana actual.

    Retorna métricas completas para inbox esta semana.
    """
    timezone_str = os.getenv("TIMEZONE", "America/Lima")
    timezone = pytz.timezone(timezone_str)
    now = datetime.now(timezone)

    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)

    return {
        "period": {"start": start_of_week.isoformat(), "end": end_of_week.isoformat()},
        "total_inbox": analytics.get_inbox_total_count(start_of_week, end_of_week),
        "by_status": analytics.get_inbox_by_status(start_of_week, end_of_week),
        "by_source": analytics.get_inbox_by_source(start_of_week, end_of_week),
        "daily_breakdown": analytics.get_inbox_daily_count(start_of_week, end_of_week),
    }


@router.get("/inbox/this-month")
def get_inbox_this_month(
    analytics: AnalyticsService = Depends(get_analytics_service),
):
    """
    Obtiene estadísticas de inbox del mes actual.

    Retorna métricas completas para inbox este mes.
    """
    timezone_str = os.getenv("TIMEZONE", "America/Lima")
    timezone = pytz.timezone(timezone_str)
    now = datetime.now(timezone)

    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    if now.month == 12:
        end_of_month = now.replace(
            year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(seconds=1)
    else:
        end_of_month = now.replace(
            month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(seconds=1)

    return {
        "period": {
            "start": start_of_month.isoformat(),
            "end": end_of_month.isoformat(),
        },
        "total_inbox": analytics.get_inbox_total_count(start_of_month, end_of_month),
        "by_status": analytics.get_inbox_by_status(start_of_month, end_of_month),
        "by_source": analytics.get_inbox_by_source(start_of_month, end_of_month),
        "daily_breakdown": analytics.get_inbox_daily_count(
            start_of_month, end_of_month
        ),
        "weekly_breakdown": analytics.get_inbox_weekly_count(
            start_of_month, end_of_month
        ),
    }
