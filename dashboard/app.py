#!/usr/bin/env python3
"""
Streamlit Dashboard for Agricultural IoT System
Displays real-time sensor data by crop zones
"""

import os
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz


# Configuration
API_DISPLAY_URL = os.getenv("API_URL", "http://localhost:5000")  # URL shown to user (from browser)
API_REQUEST_URL = API_DISPLAY_URL.replace("localhost", "api")  # URL for internal Docker requests
MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt")
MQTT_PORT = os.getenv("MQTT_PORT", "1883")

ICONOS = {"tomate": "🍅", "zanahoria": "🥕", "maiz": "🌽"}
COLORS = {"tomate": "red", "zanahoria": "orange", "maiz": "gold"}


@st.cache_data(ttl=10)
def fetch_zones():
    """Fetch available zones from API"""
    try:
        r = requests.get(f"{API_REQUEST_URL}/zonas", timeout=5)
        if r.status_code == 503:
            st.error("❌ Base de datos no conectada")
            return []
        elif r.status_code != 200:
            st.error(f"❌ Error API ({r.status_code}): {r.text[:100]}")
            return []
        
        data = r.json()
        if isinstance(data, list) and len(data) > 0:
            return data
        return []
    except requests.exceptions.Timeout:
        st.error("⏱️ Timeout: API no responde (verifica que esté corriendo en puerto 5000)")
        return []
    except requests.exceptions.ConnectionError:
        st.error("🔌 Conexión rechazada: ¿está la API corriendo? (http://localhost:5000)")
        return []
    except Exception as e:
        st.error(f"❌ Error desconocido: {str(e)[:100]}")
        return []


@st.cache_data(ttl=10)
def fetch_logs(zona=None):
    """Fetch sensor logs from API"""
    try:
        url = f"{API_REQUEST_URL}/logs/{zona}" if zona else f"{API_REQUEST_URL}/logs"
        r = requests.get(url, timeout=5)
        
        if r.status_code == 503:
            return []  # Silencioso para datos por zona
        elif r.status_code == 400:
            st.warning(f"⚠️ Parámetro inválido")
            return []
        elif r.status_code != 200:
            return []
        
        data = r.json()
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "data" in data:
            return data.get("data", [])
        return []
    except requests.exceptions.Timeout:
        return []
    except requests.exceptions.ConnectionError:
        return []
    except Exception as e:
        return []


def get_chile_time():
    """Get current time in Chile (Santiago, America/Santiago)"""
    try:
        chile_tz = pytz.timezone('America/Santiago')
        return datetime.now(chile_tz).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def show_metrics(zona, data):
    """Display key metrics for a zone"""
    if not data:
        st.info("No data available")
        return
    
    df = pd.DataFrame(data)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_temp = df["temperatura"].mean()
        st.metric("🌡️ Temp. Prom.", f"{avg_temp:.1f}°C")
    
    with col2:
        avg_humidity = df["humedad"].mean()
        st.metric("💧 Humedad Prom.", f"{avg_humidity:.1f}%")
    
    with col3:
        max_temp = df["temperatura"].max()
        st.metric("📈 Temp. Máx.", f"{max_temp:.1f}°C")
    
    with col4:
        count = len(df)
        st.metric("📊 Lecturas", count)


def show_chart(zona, data):
    """Display temperature and humidity evolution chart"""
    if not data:
        st.info("No chart data")
        return
    
    df = pd.DataFrame(data)
    
    if "timestamp" not in df.columns:
        return
    
    # Convert timestamps
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    
    # Create figure
    fig = go.Figure()
    
    # Add temperature trace
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["temperatura"],
        mode="lines+markers",
        name="Temperatura (°C)",
        line=dict(color="#EF553B", width=3),
        marker=dict(size=6),
        fill="tozeroy"
    ))
    
    # Add humidity trace
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["humedad"],
        mode="lines+markers",
        name="Humedad (%)",
        line=dict(color="#0099FF", width=3),
        marker=dict(size=6),
        fill="tozeroy",
        yaxis="y2"
    ))
    
    # Update layout
    fig.update_layout(
        title=f"Evolución - {zona.capitalize()}",
        xaxis_title="Tiempo",
        yaxis_title="Temperatura (°C)",
        yaxis2=dict(
            title="Humedad (%)",
            overlaying="y",
            side="right",
            range=[0, 100]
        ),
        hovermode="x unified",
        height=450,
        template="plotly_white",
        legend=dict(x=0.01, y=0.99)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_table(zona, data):
    """Display data table"""
    if not data:
        st.info("No table data")
        return
    
    df = pd.DataFrame(data)
    
    # Select and format columns
    cols_to_show = ["sensor_id", "zona", "temperatura", "humedad", "timestamp", "topic", "qos"]
    df_display = df[[c for c in cols_to_show if c in df.columns]].head(20).copy()
    
    # Format timestamp if present
    if "timestamp" in df_display.columns:
        df_display["timestamp"] = pd.to_datetime(df_display["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    
    st.subheader(f"📋 Últimos registros - {zona.capitalize()}")
    st.dataframe(df_display, use_container_width=True, height=300)


def main():
    """Main dashboard app"""
    # Page config
    st.set_page_config(
        page_title="IoT Agrícola",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 30px; border-radius: 10px; margin-bottom: 30px; color: white; text-align: center;">
        <h1 style="margin: 0;">🌾 Sistema IoT Agrícola</h1>
        <p style="margin: 10px 0 0 0; font-size: 18px;">Dashboard de Monitoreo Inteligente</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Display Chile time prominently at the top
        st.markdown(f"### 🕐 Hora (Chile): `{get_chile_time()}`")
        
        with st.expander("ℹ️ Información del Sistema"):
            st.write(f"**MQTT Broker:** {MQTT_BROKER}:{MQTT_PORT}")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**API Endpoint:** {API_DISPLAY_URL}")
            with col2:
                st.link_button("🔗 Acceder", API_DISPLAY_URL, use_container_width=True)
            st.write(f"**Estado:** Conectado ✓")
        
        st.divider()
        
        # Global refresh button
        if st.button("🔄 Actualizar Todos los Datos", use_container_width=True, key="global_refresh"):
            st.cache_data.clear()
            st.rerun()
    
    # Fetch zones
    zones = fetch_zones()
    
    if not zones:
        st.error("❌ No hay zonas disponibles. Verifica que los sensores estén publicando datos.")
        st.info("Los sensores deben publicar en: campo/[zona]/sensores")
        return
    
    # Create tabs
    tab_names = [f"{ICONOS.get(z, '🌱')} {z.capitalize()}" for z in zones]
    tab_names.append("🌍 Análisis Global")
    
    tabs = st.tabs(tab_names)
    
    # Individual zone tabs
    for idx, zone in enumerate(zones):
        with tabs[idx]:
            st.title(f"{ICONOS.get(zone, '🌱')} {zone.capitalize()}")
            st.markdown(f"**Topic:** `campo/{zone}/sensores` | **QoS:** 1")
            st.divider()
            
            # Fetch zone data
            zone_data = fetch_logs(zone)
            
            if zone_data:
                show_metrics(zone, zone_data)
                st.divider()
                show_chart(zone, zone_data)
                st.divider()
                show_table(zone, zone_data)
            else:
                st.warning(f"Sin datos para {zone}")
    
    # Global analysis tab
    with tabs[-1]:
        st.title("🌍 Análisis Global")
        st.markdown("Comparativa de todos los cultivos monitoreados")
        st.divider()
        
        # Fetch all data
        all_data = fetch_logs()
        
        if all_data:
            df_all = pd.DataFrame(all_data)
            
            # Global metrics
            st.subheader("📊 Métricas Globales")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("🌡️ Temp. Prom.", f"{df_all['temperatura'].mean():.1f}°C")
            with col2:
                st.metric("💧 Humedad Prom.", f"{df_all['humedad'].mean():.1f}%")
            with col3:
                st.metric("📊 Total Lecturas", len(df_all))
            with col4:
                st.metric("🔌 Sensores", df_all["sensor_id"].nunique())
            with col5:
                st.metric("🌱 Cultivos", df_all["zona"].nunique())
            
            st.divider()
            
            # Comparative chart
            st.subheader("📈 Comparativa de Temperaturas")
            
            if "timestamp" in df_all.columns:
                df_all["timestamp"] = pd.to_datetime(df_all["timestamp"])
                
                fig_comp = go.Figure()
                
                for zone in zones:
                    zone_df = df_all[df_all["zona"] == zone].sort_values("timestamp")
                    if len(zone_df) > 0:
                        fig_comp.add_trace(go.Scatter(
                            x=zone_df["timestamp"],
                            y=zone_df["temperatura"],
                            mode="lines+markers",
                            name=f"{ICONOS.get(zone)} {zone.capitalize()}",
                            line=dict(width=2)
                        ))
                
                fig_comp.update_layout(
                    title="Evolución de Temperatura por Cultivo",
                    xaxis_title="Tiempo",
                    yaxis_title="Temperatura (°C)",
                    height=400,
                    template="plotly_white",
                    hovermode="x unified",
                    legend=dict(x=0.01, y=0.99)
                )
                
                st.plotly_chart(fig_comp, use_container_width=True)
            
            st.divider()
            
            # Statistics by zone
            st.subheader("📊 Estadísticas por Cultivo")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Temperatura (°C)**")
                temp_stats = df_all.groupby("zona")["temperatura"].agg(["mean", "min", "max", "std"]).round(2)
                st.dataframe(temp_stats, use_container_width=True)
            
            with col2:
                st.write("**Humedad (%)**")
                humidity_stats = df_all.groupby("zona")["humedad"].agg(["mean", "min", "max", "std"]).round(2)
                st.dataframe(humidity_stats, use_container_width=True)
            
            st.divider()
            
            # Data table
            st.subheader("📋 Datos Consolidados")
            cols_to_show = ["sensor_id", "zona", "temperatura", "humedad", "timestamp"]
            df_display = df_all[[c for c in cols_to_show if c in df_all.columns]].head(50).copy()
            
            if "timestamp" in df_display.columns:
                df_display["timestamp"] = pd.to_datetime(df_display["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
            
            st.dataframe(df_display, use_container_width=True, height=400)
        else:
            st.warning("Sin datos disponibles")


if __name__ == "__main__":
    main()
