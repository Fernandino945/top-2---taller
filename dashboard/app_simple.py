#!/usr/bin/env python3
"""
Streamlit Dashboard for Agricultural IoT System
Displays sensor data by crop zones with metrics and visualizations
"""

import os
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta


# Configuration
API_URL = os.getenv("API_URL", "http://localhost:5000")
MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt")
MQTT_PORT = os.getenv("MQTT_PORT", "1883")
WILDCARD_TOPIC = "campo/+/sensores"

# Icons por zona
ICONOS = {
    "tomate": "🍅",
    "zanahoria": "🥕",
    "maiz": "🌽"
}


# Cache function to fetch zones dynamically
@st.cache_data(ttl=10)
def obtener_zonas():
    """Fetch available zones from API"""
    try:
        r = requests.get(f"{API_URL}/zonas", timeout=3)
        return r.json() if r.ok else []
    except Exception as e:
        st.error(f"Error fetching zones: {e}")
        return []


@st.cache_data(ttl=10)
def obtener_logs(zona=None):
    """Fetch logs from API"""
    try:
        if zona:
            url = f"{API_URL}/logs/{zona}"
        else:
            url = f"{API_URL}/logs"
        r = requests.get(url, timeout=3)
        return r.json() if r.ok else []
    except Exception as e:
        st.error(f"Error fetching logs: {e}")
        return []


def mostrar_metricas(zona, datos):
    """Display metrics for a zone"""
    if not datos:
        st.info(f"No data available for {zona}")
        return

    df = pd.DataFrame(datos)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        temp_promedio = df["temperatura"].mean()
        st.metric("🌡️ Temp. Promedio", f"{temp_promedio:.2f}°C")

    with col2:
        humedad_promedio = df["humedad"].mean()
        st.metric("💧 Humedad Promedio", f"{humedad_promedio:.2f}%")

    with col3:
        cantidad = len(df)
        st.metric("📊 Lecturas", cantidad)

    with col4:
        temp_max = df["temperatura"].max()
        st.metric("📈 Temp. Máxima", f"{temp_max:.2f}°C")


def mostrar_grafico_zona(zona, datos):
    """Display graph for a zone with colored theme"""
    if not datos:
        st.info("No data to display")
        return

    df = pd.DataFrame(datos)
    # Convert timestamp string to datetime if needed
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")

    fig = go.Figure()

    # Temperature line
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["temperatura"],
        mode="lines+markers",
        name="Temperatura (°C)",
        line=dict(color="red", width=3),
        marker=dict(size=8),
        fill="tozeroy",
        fillcolor="rgba(255, 0, 0, 0.1)"
    ))

    # Humidity line
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["humedad"],
        mode="lines+markers",
        name="Humedad (%)",
        line=dict(color="blue", width=3),
        marker=dict(size=8),
        yaxis="y2",
        fill="tozeroy",
        fillcolor="rgba(0, 0, 255, 0.1)"
    ))

    fig.update_layout(
        title=f"Evolución de Sensores - {zona.capitalize()}",
        xaxis_title="Tiempo",
        yaxis_title="Temperatura (°C)",
        yaxis2=dict(
            title="Humedad (%)",
            overlaying="y",
            side="right",
            range=[0, 100]
        ),
        hovermode="x unified",
        height=500,
        template="plotly_white",
        legend=dict(x=0.01, y=0.99),
        font=dict(size=12)
    )

    st.plotly_chart(fig, use_container_width=True)


def mostrar_tabla(zona, datos):
    """Display data table for a zone"""
    if not datos:
        st.info("No data to display")
        return

    df = pd.DataFrame(datos)
    # Convert timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp", ascending=False)
    
    # Select relevant columns
    columnas = ["sensor_id", "zona", "temperatura", "humedad", "timestamp", "topic", "qos"]
    df_mostrar = df[[col for col in columnas if col in df.columns]].head(20)
    
    # Format timestamp
    if "timestamp" in df_mostrar.columns:
        df_mostrar = df_mostrar.copy()
        df_mostrar["timestamp"] = df_mostrar["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    st.subheader(f"Últimos 20 registros - {zona.capitalize()}")
    st.dataframe(df_mostrar, use_container_width=True, height=400)


def main():
    """Main dashboard"""
    st.set_page_config(
        page_title="IoT Agrícola Dashboard",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0;">🌾 Sistema IoT Agrícola</h1>
        <h3 style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0;">Dashboard de Monitoreo Inteligente por Zonas</h3>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        with st.expander("ℹ️ Información del Sistema", expanded=True):
            st.write(f"**Broker MQTT:** `{MQTT_BROKER}:{MQTT_PORT}`")
            st.write(f"**Topic Pattern:** `{WILDCARD_TOPIC}`")
            st.write(f"**API URL:** `{API_URL}`")
            st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Auto-refresh toggle
        auto_refresh = st.checkbox("🔄 Auto-actualizar cada 10s", value=False)
        if auto_refresh:
            st.success("✓ Auto-actualización habilitada")
            import time
            time.sleep(10)
            st.rerun()

    # Fetch zones
    zonas = obtener_zonas()

    if not zonas:
        st.warning("⚠️ No hay zonas disponibles. Espera a que los sensores publiquen datos.")
        st.info("Los sensores deben estar publicando en topics: campo/tomate/sensores, etc.")
        return

    # Create tabs: one per zone + global
    tab_labels = [f"{ICONOS.get(z, '🌱')} {z.capitalize()}" for z in zonas]
    tab_labels.append("🌍 Análisis Global")

    tabs = st.tabs(tab_labels)

    # Individual zone tabs
    for idx, zona in enumerate(zonas):
        with tabs[idx]:
            st.title(f"{ICONOS.get(zona, '🌱')} {zona.capitalize()}")
            st.markdown(f"**Topic MQTT:** `campo/{zona}/sensores` | **Wildcard:** `{WILDCARD_TOPIC}`")
            st.divider()

            # Fetch zone data
            datos = obtener_logs(zona)

            if datos:
                # Metrics
                st.subheader("📊 Métricas")
                mostrar_metricas(zona, datos)

                st.divider()

                # Graph
                st.subheader("📈 Gráficos - Evolución Temporal")
                mostrar_grafico_zona(zona, datos)

                st.divider()

                # Table
                mostrar_tabla(zona, datos)
            else:
                st.info(f"Sin datos para zona: {zona}")

    # Global analysis tab
    with tabs[-1]:
        st.title("🌍 Análisis Global")
        st.markdown("**Comparativa de todos los cultivos monitoreados**")
        st.divider()

        # Fetch all data
        todos_datos = obtener_logs()

        if todos_datos:
            df_todos = pd.DataFrame(todos_datos)

            # Global metrics
            st.subheader("📊 Métricas Consolidadas")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                temp_promedio_total = df_todos["temperatura"].mean()
                st.metric("🌡️ Temp. Prom. Global", f"{temp_promedio_total:.2f}°C")
            with col2:
                humedad_promedio_total = df_todos["humedad"].mean()
                st.metric("💧 Humedad Prom. Global", f"{humedad_promedio_total:.2f}%")
            with col3:
                cantidad_total = len(df_todos)
                st.metric("📊 Total Lecturas", cantidad_total)
            with col4:
                num_sensores = df_todos["sensor_id"].nunique()
                st.metric("🔌 Sensores Activos", num_sensores)
            with col5:
                st.metric("🌱 Cultivos", len(zonas))

            st.divider()

            # Comparative graph by zone
            st.subheader("📈 Comparativa de Temperaturas")
            if "timestamp" in df_todos.columns:
                df_todos["timestamp"] = pd.to_datetime(df_todos["timestamp"])

            fig_comp = go.Figure()
            
            colores_grafico = {
                "tomate": "#EF553B",
                "zanahoria": "#FFA629",
                "maiz": "#FFD700"
            }
            
            for zona in zonas:
                df_zona = df_todos[df_todos["zona"] == zona].sort_values("timestamp")
                if len(df_zona) > 0:
                    fig_comp.add_trace(go.Scatter(
                        x=df_zona["timestamp"],
                        y=df_zona["temperatura"],
                        mode="lines+markers",
                        name=f"{ICONOS.get(zona, '🌱')} {zona.capitalize()}",
                        line=dict(color=colores_grafico.get(zona, "#999999"), width=3),
                        marker=dict(size=6)
                    ))

            fig_comp.update_layout(
                title="Evolución de Temperatura por Cultivo",
                xaxis_title="Tiempo",
                yaxis_title="Temperatura (°C)",
                hovermode="x unified",
                height=450,
                template="plotly_white",
                legend=dict(x=0.01, y=0.99)
            )
            st.plotly_chart(fig_comp, use_container_width=True)

            st.divider()

            # Statistics by zone
            st.subheader("📊 Estadísticas por Cultivo")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Temperatura Promedio por Cultivo:**")
                temp_by_zona = df_todos.groupby("zona")["temperatura"].agg(["mean", "min", "max", "std"]).round(2)
                st.dataframe(temp_by_zona, use_container_width=True)
            
            with col2:
                st.write("**Humedad Promedio por Cultivo:**")
                humedad_by_zona = df_todos.groupby("zona")["humedad"].agg(["mean", "min", "max", "std"]).round(2)
                st.dataframe(humedad_by_zona, use_container_width=True)

            st.divider()

            # Data table for all zones
            st.subheader("📋 Datos Completos de Todas las Zonas")
            columnas = ["sensor_id", "zona", "temperatura", "humedad", "timestamp", "topic", "qos"]
            df_mostrar_todos = df_todos[[col for col in columnas if col in df_todos.columns]].head(50).copy()
            
            if "timestamp" in df_mostrar_todos.columns:
                df_mostrar_todos["timestamp"] = df_mostrar_todos["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
            
            st.dataframe(df_mostrar_todos, use_container_width=True, height=500)
        else:
            st.info("Sin datos disponibles")


if __name__ == "__main__":
    main()
