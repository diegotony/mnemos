"""
Streamlit Dashboard para visualización y gestión de Mnemos.
Incluye Calendario, Ideas e Inbox.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

st.set_page_config(
    page_title="Mnemos Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Título principal
st.title("📊 Mnemos Dashboard")
st.markdown("### Gestión y visualización de tu tiempo, ideas e inbox")


# Función helper para hacer requests
def api_request(
    method: str, endpoint: str, params: dict = None, json_data: dict = None
):
    """Realiza request a la API."""
    try:
        url = f"{API_BASE_URL}/{endpoint}"
        if method == "GET":
            response = requests.get(url, params=params, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=json_data, timeout=5)
        elif method == "PUT":
            response = requests.put(url, json=json_data, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, timeout=5)
        else:
            st.error(f"Método HTTP no soportado: {method}")
            return None

        response.raise_for_status()
        return response.json() if response.content else None
    except requests.exceptions.RequestException as e:
        st.error(f"Error conectando con la API: {e}")
        return None


# Pestañas principales
tab1, tab2, tab3 = st.tabs(["📅 Calendario & Analytics", "💡 Ideas", "📥 Inbox"])


# ==================== TAB 1: CALENDARIO & ANALYTICS ====================

with tab1:
    st.sidebar.title("⚙️ Filtros - Calendario")

    # Obtener categorías disponibles
    categories_data = api_request("GET", "calendar/categories")
    available_categories = (
        ["Todas"] + list(categories_data.keys()) if categories_data else ["Todas"]
    )

    # Selector de categoría
    selected_category = st.sidebar.selectbox(
        "Categoría", available_categories, key="calendar_category"
    )

    # Mostrar info del color si hay categoría seleccionada
    if selected_category != "Todas" and categories_data:
        category_info = categories_data.get(selected_category, {})
        st.sidebar.caption(
            f"🎨 Color en Google Calendar: {category_info.get('color_name', 'N/A')}"
        )

    # Leyenda de colores
    with st.sidebar.expander("🎨 Leyenda de Colores"):
        st.markdown("**Categorías en Google Calendar:**")

        # Emojis de colores para visualización
        color_emojis = {
            "TRABAJO": "🔵",
            "SALUD": "🟢",
            "OCIO": "🔴",
            "RUTINA": "🟡",
            "PERSONAL": "💜",
            "ESTUDIO": "🔷",
            "FAMILIA": "🌸",
            "SOCIAL": "🟣",
            "SIN_CATEGORIA": "⚫",
        }

        if categories_data:
            for category, info in categories_data.items():
                emoji = color_emojis.get(category, "⭐")
                color_name = info.get("color_name", "Desconocido")
                st.markdown(f"{emoji} **{category}** - {color_name}")

        st.caption(
            "Los eventos se colorean automáticamente al sincronizar con Google Calendar"
        )

    st.sidebar.divider()

    # Selector de período
    period = st.sidebar.selectbox(
        "Período",
        [
            "Esta semana",
            "Este mes",
            "Últimos 30 días",
            "Últimos 90 días",
            "Personalizado",
        ],
        key="calendar_period",
    )

    # Fechas personalizadas
    if period == "Personalizado":
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input(
                "Desde", datetime.now() - timedelta(days=30), key="cal_start"
            )
        with col2:
            end_date = st.date_input("Hasta", datetime.now(), key="cal_end")
    else:
        start_date = None
        end_date = None

    # Determinar parámetros
    params = {}
    if period == "Personalizado":
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

    # Aplicar filtro de categoría si no es "Todas"
    if selected_category != "Todas" and selected_category != "SIN_CATEGORIA":
        # Para analytics, necesitamos filtrar después de obtener los datos
        # porque los endpoints de analytics no tienen filtro de categoría aún
        pass

    # Obtener datos
    if period == "Esta semana":
        data = api_request("GET", "analytics/this-week")
    elif period == "Este mes":
        data = api_request("GET", "analytics/this-month")
    else:
        data = {
            "time_by_category": api_request(
                "GET", "analytics/time-by-category", params
            ),
            "time_by_priority": api_request(
                "GET", "analytics/time-by-priority", params
            ),
            "productivity_metrics": api_request(
                "GET", "analytics/productivity-metrics", params
            ),
            "category_breakdown": api_request(
                "GET", "analytics/category-breakdown", params
            ),
            "daily_summary": api_request("GET", "analytics/daily-summary", params),
        }

    # Filtrar por categoría si está seleccionada
    if data and selected_category != "Todas":
        # Extraer métricas originales
        if period in ["Esta semana", "Este mes"]:
            time_by_category = data.get("time_by_category", {})
            category_breakdown = data.get("category_breakdown", {})
        else:
            time_by_category = data.get("time_by_category", {})
            category_breakdown = data.get("category_breakdown", {})

        # Filtrar solo la categoría seleccionada
        if selected_category in time_by_category:
            filtered_time_by_category = {
                selected_category: time_by_category[selected_category]
            }
            filtered_breakdown = {
                selected_category: category_breakdown.get(selected_category, {})
            }

            # Actualizar data con valores filtrados
            if period in ["Esta semana", "Este mes"]:
                data["time_by_category"] = filtered_time_by_category
                data["category_breakdown"] = filtered_breakdown
            else:
                data["time_by_category"] = filtered_time_by_category
                data["category_breakdown"] = filtered_breakdown

    if data:
        # Extraer métricas
        if period in ["Esta semana", "Este mes"]:
            productivity = data.get("productivity_metrics", {})
            time_by_category = data.get("time_by_category", {})
            time_by_priority = data.get("time_by_priority", {})
            category_breakdown = data.get("category_breakdown", {})
            daily_summary = data.get("daily_summary", [])
        else:
            productivity = data.get("productivity_metrics", {})
            time_by_category = data.get("time_by_category", {})
            time_by_priority = data.get("time_by_priority", {})
            category_breakdown = data.get("category_breakdown", {})
            daily_summary = data.get("daily_summary", [])

        # KPIs
        st.markdown("## 📈 Indicadores Clave")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_hours = productivity.get("total_hours", 0)
            st.metric("⏱️ Horas Totales", f"{total_hours:.1f}h")

        with col2:
            trabajo_hours = productivity.get("trabajo_hours", 0)
            trabajo_pct = productivity.get("trabajo_percentage", 0)
            st.metric("💼 Trabajo", f"{trabajo_hours:.1f}h", f"{trabajo_pct:.1f}%")

        with col3:
            salud_hours = productivity.get("salud_hours", 0)
            salud_pct = productivity.get("salud_percentage", 0)
            st.metric("💪 Salud", f"{salud_hours:.1f}h", f"{salud_pct:.1f}%")

        with col4:
            ocio_hours = productivity.get("ocio_hours", 0)
            ocio_pct = productivity.get("ocio_percentage", 0)
            st.metric("🎮 Ocio", f"{ocio_hours:.1f}h", f"{ocio_pct:.1f}%")

        st.divider()

        # Gráficos
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📊 Tiempo por Categoría")
            if time_by_category:
                df_category = pd.DataFrame(
                    list(time_by_category.items()), columns=["Categoría", "Horas"]
                )
                color_map = {
                    "TRABAJO": "#FF6B6B",
                    "SALUD": "#4ECDC4",
                    "OCIO": "#95E1D3",
                    "RUTINA": "#FFE66D",
                    "SIN_CATEGORIA": "#CCCCCC",
                }
                fig = px.pie(
                    df_category,
                    values="Horas",
                    names="Categoría",
                    hole=0.4,
                    color="Categoría",
                    color_discrete_map=color_map,
                )
                fig.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de categorías")

        with col2:
            st.markdown("### 🎯 Tiempo por Prioridad")
            if time_by_priority:
                df_priority = pd.DataFrame(
                    list(time_by_priority.items()), columns=["Prioridad", "Horas"]
                )
                priority_colors = {
                    "critical": "#D32F2F",
                    "high": "#F57C00",
                    "medium": "#FDD835",
                    "low": "#388E3C",
                    "SIN_PRIORIDAD": "#9E9E9E",
                }
                fig = px.bar(
                    df_priority,
                    x="Prioridad",
                    y="Horas",
                    color="Prioridad",
                    color_discrete_map=priority_colors,
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de prioridades")

        st.divider()

        # Información sobre colores en Google Calendar
        with st.expander("🎨 Colores en Google Calendar"):
            st.markdown("""
            **Tus eventos se colorean automáticamente en Google Calendar según su categoría:**
            
            - 🔵 **TRABAJO** → Azul (Arándano)
            - 🟢 **SALUD** → Verde (Albahaca)  
            - 🔴 **OCIO** → Rojo (Tomate)
            - 🟡 **RUTINA** → Amarillo (Banana)
            - 💜 **PERSONAL** → Lavanda
            - 🔷 **ESTUDIO** → Cyan (Pavo real)
            - 🌸 **FAMILIA** → Rosado (Flamingo)
            - 🟣 **SOCIAL** → Púrpura (Uva)
            - ⚫ **SIN_CATEGORIA** → Gris (Grafito)
            
            Los colores se aplican automáticamente al sincronizar eventos con Google Calendar.
            """)

        st.divider()

        # Resumen diario
        st.markdown("### 📅 Resumen Diario")
        if daily_summary:
            df_daily = pd.DataFrame(daily_summary)
            df_daily["date"] = pd.to_datetime(df_daily["date"])

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=df_daily["date"],
                    y=df_daily["total_hours"],
                    mode="lines+markers",
                    name="Horas Totales",
                    line=dict(color="#4ECDC4", width=3),
                    marker=dict(size=8),
                )
            )
            fig.update_layout(
                title="Evolución Diaria de Horas",
                xaxis_title="Fecha",
                yaxis_title="Horas",
                hovermode="x unified",
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("📋 Ver datos detallados"):
                st.dataframe(df_daily, use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos diarios")

        st.divider()

        # Desglose por categoría
        st.markdown("### 🔍 Desglose Detallado")
        if category_breakdown:
            breakdown_data = []
            for category, stats in category_breakdown.items():
                breakdown_data.append(
                    {
                        "Categoría": category,
                        "Horas Totales": stats["total_hours"],
                        "Eventos": stats["event_count"],
                        "Promedio": stats["avg_hours_per_event"],
                        "% del Total": stats["percentage_of_total"],
                    }
                )
            df_breakdown = pd.DataFrame(breakdown_data).sort_values(
                "Horas Totales", ascending=False
            )
            st.dataframe(df_breakdown, use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos de desglose")


# ==================== TAB 2: IDEAS ====================

with tab2:
    st.markdown("## 💡 Gestión de Ideas")

    # Crear dos pestañas secundarias: Gestión y Analytics
    subtab1, subtab2 = st.tabs(["📝 Gestión", "📊 Estadísticas"])

    with subtab1:
        st.markdown("### 📝 Gestión de Ideas")

        # Formulario para crear nueva idea
        with st.expander("➕ Crear Nueva Idea"):
            with st.form("new_idea_form"):
                new_idea_content = st.text_area(
                    "Contenido de la idea", placeholder="Escribe tu idea aquí..."
                )
                submitted = st.form_submit_button("Crear Idea")

                if submitted and new_idea_content:
                    result = api_request(
                        "POST", "ideas", json_data={"content": new_idea_content}
                    )
                    if result:
                        st.success("✅ Idea creada exitosamente")
                        st.rerun()

        # Listar ideas existentes
        ideas = api_request("GET", "ideas")

        if ideas:
            st.markdown(f"**Total de ideas:** {len(ideas)}")

            for idea in ideas:
                with st.container():
                    col1, col2 = st.columns([5, 1])

                    with col1:
                        # Editar idea inline
                        new_content = st.text_area(
                            f"Idea #{idea['id']}",
                            value=idea["content"],
                            key=f"idea_{idea['id']}",
                            height=100,
                        )
                        st.caption(f"Creada: {idea['created_at']}")

                    with col2:
                        # Botones de acción
                        if st.button("💾", key=f"save_{idea['id']}", help="Guardar"):
                            if new_content != idea["content"]:
                                result = api_request(
                                    "PUT",
                                    f"ideas/{idea['id']}",
                                    json_data={"content": new_content},
                                )
                                if result:
                                    st.success("Guardado")
                                    st.rerun()

                        if st.button("🗑️", key=f"delete_{idea['id']}", help="Eliminar"):
                            result = api_request("DELETE", f"ideas/{idea['id']}")
                            if result:
                                st.success("Eliminada")
                                st.rerun()

                    st.divider()
        else:
            st.info("No hay ideas registradas")

    with subtab2:
        st.markdown("### 📊 Estadísticas de Ideas")

        # Filtros
        period_ideas = st.selectbox(
            "Período", ["Esta semana", "Este mes", "Todo"], key="ideas_period"
        )

        # Obtener datos
        if period_ideas == "Esta semana":
            ideas_stats = api_request("GET", "analytics/ideas/this-week")
        elif period_ideas == "Este mes":
            ideas_stats = api_request("GET", "analytics/ideas/this-month")
        else:
            ideas_stats = {
                "total_ideas": api_request("GET", "analytics/ideas/total"),
                "daily_breakdown": api_request("GET", "analytics/ideas/daily"),
            }

        if ideas_stats:
            # Métricas
            total = ideas_stats.get("total_ideas", ideas_stats.get("total_ideas", 0))
            st.metric("💡 Total de Ideas", total)

            # Gráfico diario
            daily_data = ideas_stats.get("daily_breakdown", [])
            if daily_data:
                st.markdown("#### 📅 Ideas por Día")
                df_ideas_daily = pd.DataFrame(daily_data)
                df_ideas_daily["date"] = pd.to_datetime(df_ideas_daily["date"])

                fig = px.bar(
                    df_ideas_daily, x="date", y="count", title="Ideas Creadas por Día"
                )
                st.plotly_chart(fig, use_container_width=True)

            # Gráfico semanal
            weekly_data = ideas_stats.get("weekly_breakdown", [])
            if weekly_data:
                st.markdown("#### 📊 Ideas por Semana")
                df_ideas_weekly = pd.DataFrame(weekly_data)
                df_ideas_weekly["label"] = df_ideas_weekly.apply(
                    lambda x: f"{x['year']}-W{x['week']:02d}", axis=1
                )

                fig = px.bar(
                    df_ideas_weekly,
                    x="label",
                    y="count",
                    title="Ideas Creadas por Semana",
                )
                st.plotly_chart(fig, use_container_width=True)


# ==================== TAB 3: INBOX ====================

with tab3:
    st.markdown("## 📥 Gestión de Inbox")

    # Crear dos pestañas secundarias
    subtab1, subtab2 = st.tabs(["📝 Gestión", "📊 Estadísticas"])

    with subtab1:
        st.markdown("### 📝 Gestión de Inbox")

        # Formulario para crear nuevo inbox item
        with st.expander("➕ Crear Nuevo Item"):
            with st.form("new_inbox_form"):
                new_inbox_content = st.text_area(
                    "Contenido", placeholder="¿Qué quieres guardar en el inbox?"
                )
                new_inbox_source = st.selectbox(
                    "Fuente", ["manual", "cli", "web", "discord"]
                )
                submitted = st.form_submit_button("Crear Item")

                if submitted and new_inbox_content:
                    result = api_request(
                        "POST",
                        "inbox",
                        json_data={
                            "content": new_inbox_content,
                            "source": new_inbox_source,
                        },
                    )
                    if result:
                        st.success("✅ Item creado exitosamente")
                        st.rerun()

        # Listar inbox items
        inbox_items = api_request("GET", "inbox")

        if inbox_items:
            st.markdown(f"**Total de items:** {len(inbox_items)}")

            for item in inbox_items:
                with st.container():
                    col1, col2 = st.columns([5, 1])

                    with col1:
                        # Mostrar item
                        st.text_area(
                            f"Item #{item['id']}",
                            value=item["content"],
                            key=f"inbox_{item['id']}",
                            height=100,
                            disabled=True,
                        )
                        st.caption(
                            f"Fuente: {item.get('source', 'N/A')} | Creado: {item['created_at']}"
                        )

                    with col2:
                        # Botón de eliminar
                        if st.button(
                            "🗑️", key=f"delete_inbox_{item['id']}", help="Eliminar"
                        ):
                            result = api_request("DELETE", f"inbox/{item['id']}")
                            if result:
                                st.success("Eliminado")
                                st.rerun()

                    st.divider()
        else:
            st.info("No hay items en el inbox")

    with subtab2:
        st.markdown("### 📊 Estadísticas de Inbox")

        # Filtros
        period_inbox = st.selectbox(
            "Período", ["Esta semana", "Este mes", "Todo"], key="inbox_period"
        )

        # Obtener datos
        if period_inbox == "Esta semana":
            inbox_stats = api_request("GET", "analytics/inbox/this-week")
        elif period_inbox == "Este mes":
            inbox_stats = api_request("GET", "analytics/inbox/this-month")
        else:
            inbox_stats = {
                "total_inbox": api_request("GET", "analytics/inbox/total"),
                "by_status": api_request("GET", "analytics/inbox/by-status"),
                "by_source": api_request("GET", "analytics/inbox/by-source"),
                "daily_breakdown": api_request("GET", "analytics/inbox/daily"),
            }

        if inbox_stats:
            # Métricas
            total = inbox_stats.get("total_inbox", inbox_stats.get("total_inbox", 0))
            st.metric("📥 Total de Items", total)

            # Gráficos
            col1, col2 = st.columns(2)

            with col1:
                # Por fuente
                by_source = inbox_stats.get("by_source", {})
                if by_source:
                    st.markdown("#### 📌 Por Fuente")
                    df_source = pd.DataFrame(
                        list(by_source.items()), columns=["Fuente", "Cantidad"]
                    )
                    fig = px.pie(df_source, values="Cantidad", names="Fuente", hole=0.4)
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Por estado
                by_status = inbox_stats.get("by_status", {})
                if by_status:
                    st.markdown("#### 🏷️ Por Estado")
                    df_status = pd.DataFrame(
                        list(by_status.items()), columns=["Estado", "Cantidad"]
                    )
                    fig = px.bar(df_status, x="Estado", y="Cantidad")
                    st.plotly_chart(fig, use_container_width=True)

            # Gráfico diario
            daily_data = inbox_stats.get("daily_breakdown", [])
            if daily_data:
                st.markdown("#### 📅 Items por Día")
                df_inbox_daily = pd.DataFrame(daily_data)
                df_inbox_daily["date"] = pd.to_datetime(df_inbox_daily["date"])

                fig = px.bar(
                    df_inbox_daily, x="date", y="count", title="Items Creados por Día"
                )
                st.plotly_chart(fig, use_container_width=True)

            # Gráfico semanal
            weekly_data = inbox_stats.get("weekly_breakdown", [])
            if weekly_data:
                st.markdown("#### 📊 Items por Semana")
                df_inbox_weekly = pd.DataFrame(weekly_data)
                df_inbox_weekly["label"] = df_inbox_weekly.apply(
                    lambda x: f"{x['year']}-W{x['week']:02d}", axis=1
                )

                fig = px.bar(
                    df_inbox_weekly,
                    x="label",
                    y="count",
                    title="Items Creados por Semana",
                )
                st.plotly_chart(fig, use_container_width=True)


# ==================== FOOTER ====================

st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: gray;'>
    <p>Mnemos Dashboard • Datos en tiempo real</p>
</div>
""",
    unsafe_allow_html=True,
)

# Botón de refresh en sidebar
if st.sidebar.button("🔄 Actualizar"):
    st.rerun()
