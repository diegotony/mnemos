"""
Servicio de Analytics para calcular estadísticas de eventos.
Provee métricas sobre uso del tiempo por categoría, prioridad, etc.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, case, text
from models.calendar_event import CalendarEvent
from models.idea import Idea
from models.inbox_item import InboxItem
import pytz


class AnalyticsService:
    """Servicio para calcular estadísticas y métricas de eventos."""

    def __init__(self, db: Session, timezone: str = "America/Lima"):
        self.db = db
        self.timezone = pytz.timezone(timezone)

    def _calculate_hours_in_python(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[CalendarEvent]:
        """
        Obtiene eventos y calcula horas en Python (compatible con SQLite y PostgreSQL).

        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)

        Returns:
            Lista de eventos filtrados
        """
        query = self.db.query(CalendarEvent)

        if start_date:
            query = query.filter(CalendarEvent.start_datetime >= start_date)
        if end_date:
            query = query.filter(CalendarEvent.end_datetime <= end_date)

        return query.all()

    def get_time_by_category(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, float]:
        """
        Calcula tiempo total (en horas) por categoría.

        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)

        Returns:
            Dict con categoría -> horas totales
        """
        events = self._calculate_hours_in_python(start_date, end_date)

        category_hours: Dict[str, float] = {}

        for event in events:
            duration = event.end_datetime - event.start_datetime
            hours = duration.total_seconds() / 3600

            category = event.category or "SIN_CATEGORIA"  # type: ignore
            category_hours[category] = category_hours.get(category, 0) + hours

        return category_hours

    def get_time_by_priority(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, float]:
        """
        Calcula tiempo total (en horas) por prioridad.

        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)

        Returns:
            Dict con prioridad -> horas totales
        """
        events = self._calculate_hours_in_python(start_date, end_date)

        priority_hours: Dict[str, float] = {}

        for event in events:
            duration = event.end_datetime - event.start_datetime
            hours = duration.total_seconds() / 3600

            priority = event.priority or "SIN_PRIORIDAD"  # type: ignore
            priority_hours[priority] = priority_hours.get(priority, 0) + hours

        return priority_hours

    def get_event_count_by_category(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, int]:
        """
        Cuenta número de eventos por categoría.

        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)

        Returns:
            Dict con categoría -> número de eventos
        """
        query = self.db.query(
            CalendarEvent.category, func.count(CalendarEvent.id).label("event_count")
        )

        if start_date:
            query = query.filter(CalendarEvent.start_datetime >= start_date)
        if end_date:
            query = query.filter(CalendarEvent.end_datetime <= end_date)

        query = query.group_by(CalendarEvent.category)

        results = query.all()

        return {
            row.category or "SIN_CATEGORIA": int(row.event_count) for row in results
        }

    def get_daily_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """
        Obtiene resumen diario de horas trabajadas.

        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)

        Returns:
            Lista de dicts con {date, total_hours, event_count}
        """
        events = self._calculate_hours_in_python(start_date, end_date)

        daily_data: Dict[str, Dict] = {}

        for event in events:
            duration = event.end_datetime - event.start_datetime
            hours = duration.total_seconds() / 3600

            # Obtener fecha como string (YYYY-MM-DD)
            date_str = event.start_datetime.date().isoformat()

            if date_str not in daily_data:
                daily_data[date_str] = {"total_hours": 0, "event_count": 0}

            daily_data[date_str]["total_hours"] += hours
            daily_data[date_str]["event_count"] += 1

        # Convertir a lista ordenada
        result = [
            {
                "date": date,
                "total_hours": data["total_hours"],
                "event_count": data["event_count"],
            }
            for date, data in sorted(daily_data.items())
        ]

        return result

    def get_weekly_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """
        Obtiene resumen semanal de horas trabajadas.

        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)

        Returns:
            Lista de dicts con {week, year, total_hours, event_count}
        """
        events = self._calculate_hours_in_python(start_date, end_date)

        weekly_data: Dict[tuple, Dict] = {}

        for event in events:
            duration = event.end_datetime - event.start_datetime
            hours = duration.total_seconds() / 3600

            # Obtener año y semana (ISO 8601)
            year, week, _ = event.start_datetime.isocalendar()
            key = (year, week)

            if key not in weekly_data:
                weekly_data[key] = {"total_hours": 0, "event_count": 0}

            weekly_data[key]["total_hours"] += hours
            weekly_data[key]["event_count"] += 1

        # Convertir a lista ordenada
        result = [
            {
                "year": year,
                "week": week,
                "total_hours": data["total_hours"],
                "event_count": data["event_count"],
            }
            for (year, week), data in sorted(weekly_data.items())
        ]

        return result

    def get_category_breakdown(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict:
        """
        Obtiene desglose completo por categoría.

        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)

        Returns:
            Dict con estadísticas por categoría
        """
        time_by_category = self.get_time_by_category(start_date, end_date)
        count_by_category = self.get_event_count_by_category(start_date, end_date)

        total_hours = sum(time_by_category.values())

        breakdown = {}
        for category in set(
            list(time_by_category.keys()) + list(count_by_category.keys())
        ):
            hours = time_by_category.get(category, 0)
            count = count_by_category.get(category, 0)

            breakdown[category] = {
                "total_hours": hours,
                "event_count": count,
                "avg_hours_per_event": hours / count if count > 0 else 0,
                "percentage_of_total": (hours / total_hours * 100)
                if total_hours > 0
                else 0,
            }

        return breakdown

    def get_productivity_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict:
        """
        Calcula métricas de productividad.

        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)

        Returns:
            Dict con métricas de productividad
        """
        time_by_category = self.get_time_by_category(start_date, end_date)
        time_by_priority = self.get_time_by_priority(start_date, end_date)

        total_hours = sum(time_by_category.values())
        trabajo_hours = time_by_category.get("TRABAJO", 0)
        salud_hours = time_by_category.get("SALUD", 0)
        ocio_hours = time_by_category.get("OCIO", 0)

        high_priority_hours = time_by_priority.get("high", 0) + time_by_priority.get(
            "critical", 0
        )

        return {
            "total_hours": total_hours,
            "trabajo_hours": trabajo_hours,
            "salud_hours": salud_hours,
            "ocio_hours": ocio_hours,
            "trabajo_percentage": (trabajo_hours / total_hours * 100)
            if total_hours > 0
            else 0,
            "salud_percentage": (salud_hours / total_hours * 100)
            if total_hours > 0
            else 0,
            "ocio_percentage": (ocio_hours / total_hours * 100)
            if total_hours > 0
            else 0,
            "high_priority_hours": high_priority_hours,
            "high_priority_percentage": (high_priority_hours / total_hours * 100)
            if total_hours > 0
            else 0,
        }

    def get_time_usage_trends(self, days: int = 30) -> Dict:
        """
        Analiza tendencias de uso del tiempo en los últimos N días.

        Args:
            days: Número de días hacia atrás (default: 30)

        Returns:
            Dict con tendencias y comparaciones
        """
        now = datetime.now(self.timezone)
        period_start = now - timedelta(days=days)

        # Métricas actuales (últimos N días)
        current_metrics = self.get_productivity_metrics(period_start, now)

        # Métricas anteriores (N días previos)
        previous_start = period_start - timedelta(days=days)
        previous_metrics = self.get_productivity_metrics(previous_start, period_start)

        # Calcular cambios
        def calculate_change(current: float, previous: float) -> Dict:
            if previous == 0:
                return {"value": current, "change": 0, "change_percentage": 0}

            change = current - previous
            change_percentage = (change / previous) * 100

            return {
                "value": current,
                "change": change,
                "change_percentage": change_percentage,
            }

        return {
            "period_days": days,
            "current_period": {
                "start": period_start.isoformat(),
                "end": now.isoformat(),
            },
            "total_hours": calculate_change(
                current_metrics["total_hours"], previous_metrics["total_hours"]
            ),
            "trabajo_hours": calculate_change(
                current_metrics["trabajo_hours"], previous_metrics["trabajo_hours"]
            ),
            "salud_hours": calculate_change(
                current_metrics["salud_hours"], previous_metrics["salud_hours"]
            ),
            "ocio_hours": calculate_change(
                current_metrics["ocio_hours"], previous_metrics["ocio_hours"]
            ),
        }

    # ========== IDEAS ANALYTICS ==========

    def get_ideas_total_count(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        """
        Cuenta el total de ideas creadas.

        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)

        Returns:
            Número total de ideas
        """
        query = self.db.query(func.count(Idea.id))

        if start_date:
            query = query.filter(Idea.created_at >= start_date)
        if end_date:
            query = query.filter(Idea.created_at <= end_date)

        return query.scalar() or 0

    def get_ideas_daily_count(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """
        Obtiene conteo diario de ideas creadas.

        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)

        Returns:
            Lista de dicts con {date, count}
        """
        query = self.db.query(Idea)

        if start_date:
            query = query.filter(Idea.created_at >= start_date)
        if end_date:
            query = query.filter(Idea.created_at <= end_date)

        ideas = query.all()

        daily_counts: Dict[str, int] = {}

        for idea in ideas:
            date_str = idea.created_at.date().isoformat()
            daily_counts[date_str] = daily_counts.get(date_str, 0) + 1

        result = [
            {"date": date, "count": count}
            for date, count in sorted(daily_counts.items())
        ]

        return result

    def get_ideas_weekly_count(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """
        Obtiene conteo semanal de ideas creadas.

        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)

        Returns:
            Lista de dicts con {year, week, count}
        """
        query = self.db.query(Idea)

        if start_date:
            query = query.filter(Idea.created_at >= start_date)
        if end_date:
            query = query.filter(Idea.created_at <= end_date)

        ideas = query.all()

        weekly_counts: Dict[tuple, int] = {}

        for idea in ideas:
            year, week, _ = idea.created_at.isocalendar()
            key = (year, week)
            weekly_counts[key] = weekly_counts.get(key, 0) + 1

        result = [
            {"year": year, "week": week, "count": count}
            for (year, week), count in sorted(weekly_counts.items())
        ]

        return result

    # ========== INBOX ANALYTICS ==========

    def get_inbox_total_count(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        """
        Cuenta el total de inbox items.

        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)

        Returns:
            Número total de inbox items
        """
        query = self.db.query(func.count(InboxItem.id))

        if start_date:
            query = query.filter(InboxItem.created_at >= start_date)
        if end_date:
            query = query.filter(InboxItem.created_at <= end_date)

        return query.scalar() or 0

    def get_inbox_by_status(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, int]:
        """
        Cuenta inbox items por status.

        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)

        Returns:
            Dict con status_id -> count
        """
        query = self.db.query(InboxItem)

        if start_date:
            query = query.filter(InboxItem.created_at >= start_date)
        if end_date:
            query = query.filter(InboxItem.created_at <= end_date)

        items = query.all()

        status_counts: Dict[str, int] = {}

        for item in items:
            status = str(item.status_id) if item.status_id else "SIN_STATUS"  # type: ignore
            status_counts[status] = status_counts.get(status, 0) + 1

        return status_counts

    def get_inbox_by_source(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, int]:
        """
        Cuenta inbox items por source.

        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)

        Returns:
            Dict con source -> count
        """
        query = self.db.query(InboxItem)

        if start_date:
            query = query.filter(InboxItem.created_at >= start_date)
        if end_date:
            query = query.filter(InboxItem.created_at <= end_date)

        items = query.all()

        source_counts: Dict[str, int] = {}

        for item in items:
            source = str(item.source) if item.source else "UNKNOWN"  # type: ignore
            source_counts[source] = source_counts.get(source, 0) + 1

        return source_counts

    def get_inbox_daily_count(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """
        Obtiene conteo diario de inbox items.

        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)

        Returns:
            Lista de dicts con {date, count}
        """
        query = self.db.query(InboxItem)

        if start_date:
            query = query.filter(InboxItem.created_at >= start_date)
        if end_date:
            query = query.filter(InboxItem.created_at <= end_date)

        items = query.all()

        daily_counts: Dict[str, int] = {}

        for item in items:
            date_str = item.created_at.date().isoformat()
            daily_counts[date_str] = daily_counts.get(date_str, 0) + 1

        result = [
            {"date": date, "count": count}
            for date, count in sorted(daily_counts.items())
        ]

        return result

    def get_inbox_weekly_count(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """
        Obtiene conteo semanal de inbox items.

        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)

        Returns:
            Lista de dicts con {year, week, count}
        """
        query = self.db.query(InboxItem)

        if start_date:
            query = query.filter(InboxItem.created_at >= start_date)
        if end_date:
            query = query.filter(InboxItem.created_at <= end_date)

        items = query.all()

        weekly_counts: Dict[tuple, int] = {}

        for item in items:
            year, week, _ = item.created_at.isocalendar()
            key = (year, week)
            weekly_counts[key] = weekly_counts.get(key, 0) + 1

        result = [
            {"year": year, "week": week, "count": count}
            for (year, week), count in sorted(weekly_counts.items())
        ]

        return result
