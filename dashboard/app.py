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
API_URL = "http://localhost:5000"  # Always use localhost for browser compatibility
MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt")
MQTT_PORT = os.getenv("MQTT_PORT", "1883")

ICONOS = {"tomate": "🍅", "zanahoria": "🥕", "maiz": "🌽"}
COLORS = {"tomate": "red", "zanahoria": "orange", "maiz": "gold"}


@st.cache_data(ttl=10)
def fetch_zones():
    """Fetch available zones from API"""
    try:
        r = requests.get(f"{API_URL}/zonas", timeout=5)
        return r.json() if r.ok else []
    except Exception as e:
        st.error(f"Error fetching zones: {e}")
        return []


@st.cache_data(ttl=10)
def fetch_logs(zona=None):
    """Fetch sensor logs from API"""
    try:
        url = f"{API_URL}/logs/{zona}" if zona else f"{API_URL}/logs"
        r = requests.get(url, timeout=5)
        return r.json() if r.ok else []
    except Exception as e:
        st.error(f"Error fetching logs: {e}")
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
            st.write(f"**API Endpoint:** {API_URL}")
            st.write(f"**Estado:** Conectado ✓")
        
        st.divider()
        
        # Auto-refresh option
        refresh = st.checkbox("⏱️ Auto-actualizar (10s)", value=False)
        if refresh:
            import time
            st.info("Auto-actualización en 10s...")
            time.sleep(10)
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
            
            # Refresh button for this zone
            if st.button(f"🔄 Actualizar gráfico de {zone.capitalize()}", use_container_width=True, key=f"refresh_{zone}"):
                st.cache_data.clear()
                st.rerun()
            
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
#!/usr/bin/env python3
"""
Streamlit Dashboard for Agricultural IoT System
"""

import os
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:5000")
MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt")
MQTT_PORT = os.getenv("MQTT_PORT", "1883")

ICONOS = {"tomate": "🍅", "zanahoria": "🥕", "maiz": "🌽"}

@st.cache_data(ttl=10)
def obtener_zonas():
    try:
        r = requests.get(f"{API_URL}/zonas", timeout=3)
        return r.json() if r.ok else []
    except:
        return []

@st.cache_data(ttl=10)
def obtener_logs(zona=None):
    try:
        url = f"{API_URL}/logs/{zona}" if zona else f"{API_URL}/logs"
        r = requests.get(url, timeout=3)
        return r.json() if r.ok else []
    except:
        return []

def mostrar_metricas(zona, datos):
    if not datos:
        return
    df = pd.DataFrame(datos)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🌡️ Temp. Prom.", f"{df['temperatura'].mean():.2f}°C")
    with col2:
        st.metric("💧 Humedad Prom.", f"{df['humedad'].mean():.2f}%")
    with col3:
        st.metric("📈 Temp. Máx.", f"{df['temperatura'].max():.2f}°C")
    with col4:
        st.metric("📊 Lecturas", len(df))

def mostrar_grafico(zona, datos):
    if not datos:
        return
    df = pd.DataFrame(datos)
    if "timestamp" not in df.columns:
        return
    
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["temperatura"], 
                            mode="lines+markers", name="Temperatura (°C)", 
                            line=dict(color="red", width=2)))
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["humedad"], 
                            mode="lines+markers", name="Humedad (%)", 
                            line=dict(color="blue", width=2), yaxis="y2"))
    
    fig.update_layout(
        title=f"{zona.capitalize()} - Evolución",
        xaxis_title="Tiempo",
        yaxis_title="Temperatura (°C)",
        yaxis2=dict(title="Humedad (%)", overlaying="y", side="right"),
        height=400,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

def mostrar_tabla(zona, datos):
    if not datos:
        return
    df = pd.DataFrame(datos)
    cols = ["sensor_id", "zona", "temperatura", "humedad", "timestamp", "topic", "qos"]
    df = df[[c for c in cols if c in df.columns]].head(20)
    st.subheader(f"Últimos registros - {zona.capitalize()}")
    st.dataframe(df, use_container_width=True)

def main():
    st.set_page_config(page_title="IoT Agrícola", page_icon="🌾", layout="wide")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px; color: white;">
        <h1>🌾 Sistema IoT Agrícola</h1>
        <p>Dashboard de Monitoreo Inteligente</p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️ Sistema")
        st.write(f"**Broker MQTT:** {MQTT_BROKER}:{MQTT_PORT}")
        st.write(f"**API URL:** {API_URL}")
        auto_refresh = st.checkbox("🔄 Auto-actualizar (10s)")
        if auto_refresh:
            import time
            time.sleep(10)
            st.rerun()

    zonas = obtener_zonas()
    if not zonas:
        st.error("No hay datos disponibles")
        return

    tabs = st.tabs([f"{ICONOS.get(z, '🌱')} {z.capitalize()}" for z in zonas] + ["🌍 Global"])

    for idx, zona in enumerate(zonas):
        with tabs[idx]:
            st.title(f"{ICONOS.get(zona)} {zona.capitalize()}")
            datos = obtener_logs(zona)
            if datos:
                mostrar_metricas(zona, datos)
                st.divider()
                mostrar_grafico(zona, datos)
                st.divider()
                mostrar_tabla(zona, datos)

    with tabs[-1]:
        st.title("🌍 Análisis Global")
        todos = obtener_logs()
        if todos:
            df = pd.DataFrame(todos)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Temp. Prom.", f"{df['temperatura'].mean():.2f}°C")
            with col2:
                st.metric("Humedad Prom.", f"{df['humedad'].mean():.2f}%")
            with col3:
                st.metric("Total Lecturas", len(df))
            with col4:
                st.metric("Cultivos", df['zona'].nunique())
            
            st.divider()
            st.subheader("Comparativa")
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                fig = go.Figure()
                for zona in zonas:
                    dz = df[df["zona"] == zona].sort_values("timestamp")
                    fig.add_trace(go.Scatter(x=dz["timestamp"], y=dz["temperatura"],
                                           mode="lines", name=zona.capitalize()))
                fig.update_layout(title="Temperatura por Cultivo", height=400, template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            st.subheader("Datos")
            cols = ["sensor_id", "zona", "temperatura", "humedad", "timestamp"]
            st.dataframe(df[[c for c in cols if c in df.columns]].head(30), use_container_width=True)

if __name__ == "__main__":
    main()
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
    """Display enhanced graphs for a zone"""
    if not datos:
        st.info("No data to display")
        return

    df = pd.DataFrame(datos)
    # Convert timestamp string to datetime if needed
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")

    # Tab for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Serie Temporal", "📊 Distribución", "🔄 Correlación", "⏱️ Boxplot"])
    
    with tab1:
        # Temperature and Humidity over time with dual axis
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["temperatura"],
            mode="lines+markers",
            name="Temperatura (°C)",
            line=dict(color="#EF553B", width=3),
            marker=dict(size=8),
            fill="tozeroy",
            fillcolor="rgba(239, 85, 59, 0.2)"
        ))

        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["humedad"],
            mode="lines+markers",
            name="Humedad (%)",
            line=dict(color="#0099ff", width=3),
            marker=dict(size=8),
            yaxis="y2",
            fill="tozeroy",
            fillcolor="rgba(0, 153, 255, 0.2)"
        ))

        fig.update_layout(
            title=f"Evolución Temporal - {zona.capitalize()}",
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
    
    with tab2:
        # Distribution histograms
        col1, col2 = st.columns(2)
        
        with col1:
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Histogram(
                x=df["temperatura"],
                name="Temperatura",
                marker_color="#EF553B",
                nbinsx=20
            ))
            fig_temp.update_layout(
                title="Distribución de Temperaturas",
                xaxis_title="Temperatura (°C)",
                yaxis_title="Frecuencia",
                height=400,
                template="plotly_white"
            )
            st.plotly_chart(fig_temp, use_container_width=True)
        
        with col2:
            fig_hum = go.Figure()
            fig_hum.add_trace(go.Histogram(
                x=df["humedad"],
                name="Humedad",
                marker_color="#0099ff",
                nbinsx=20
            ))
            fig_hum.update_layout(
                title="Distribución de Humedad",
                xaxis_title="Humedad (%)",
                yaxis_title="Frecuencia",
                height=400,
                template="plotly_white"
            )
            st.plotly_chart(fig_hum, use_container_width=True)
    
    with tab3:
        # Scatter plot showing temperature vs humidity correlation
        fig_corr = go.Figure()
        fig_corr.add_trace(go.Scatter(
            x=df["temperatura"],
            y=df["humedad"],
            mode="markers",
            marker=dict(
                size=10,
                color=df["temperatura"],
                colorscale="Viridis",
                showscale=True,
                colorbar=dict(title="Temp (°C)")
            ),
            name="Puntos"
        ))
        
        # Add trend line
        z = np.polyfit(df["temperatura"].dropna(), df["humedad"].dropna(), 1)
        p = np.poly1d(z)
        x_trend = np.linspace(df["temperatura"].min(), df["temperatura"].max(), 100)
        fig_corr.add_trace(go.Scatter(
            x=x_trend,
            y=p(x_trend),
            mode="lines",
            name="Tendencia",
            line=dict(color="red", dash="dash")
        ))
        
        fig_corr.update_layout(
            title="Correlación: Temperatura vs Humedad",
            xaxis_title="Temperatura (°C)",
            yaxis_title="Humedad (%)",
            height=400,
            template="plotly_white"
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    
    with tab4:
        # Boxplot
        fig_box = go.Figure()
        fig_box.add_trace(go.Box(
            y=df["temperatura"],
            name="Temperatura (°C)",
            marker_color="#EF553B"
        ))
        fig_box.add_trace(go.Box(
            y=df["humedad"],
            name="Humedad (%)",
            marker_color="#0099ff"
        ))
        
        fig_box.update_layout(
            title="Análisis de Dispersión",
            height=400,
            template="plotly_white"
        )
        st.plotly_chart(fig_box, use_container_width=True)


def mostrar_tabla(zona, datos):
    """Display enhanced data table for a zone"""
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
    
    # Format display
    if "timestamp" in df_mostrar.columns:
        df_mostrar["timestamp"] = df_mostrar["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    
    st.subheader(f"📋 Últimos 20 Registros - {zona.capitalize()}")
    st.dataframe(
        df_mostrar,
        use_container_width=True,
        height=400,
        column_config={
            "temperatura": st.column_config.NumberColumn(format="%.2f °C"),
            "humedad": st.column_config.NumberColumn(format="%.2f %%"),
            "qos": st.column_config.NumberColumn(format="%d")
        }
    )


def aplica_filtros(df, fecha_inicio, fecha_fin, temp_min, temp_max, humedad_min, humedad_max):
    """Apply filters to dataframe"""
    # Convert timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    # Apply filters
    mask = (
        (df["timestamp"] >= fecha_inicio) &
        (df["timestamp"] <= fecha_fin) &
        (df["temperatura"] >= temp_min) &
        (df["temperatura"] <= temp_max) &
        (df["humedad"] >= humedad_min) &
        (df["humedad"] <= humedad_max)
    )
    
    return df[mask]


def main():
    """Main dashboard with enhanced UI"""
    st.set_page_config(
        page_title="IoT Agrícola Dashboard",
        page_icon="🌾",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Apply custom CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # Header with gradient (using markdown with colors)
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0;">🌾 Sistema IoT Agrícola</h1>
        <h3 style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0;">Dashboard de Monitoreo Inteligente</h3>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración del Sistema")
        
        with st.expander("ℹ️ Información", expanded=True):
            st.write(f"**Broker MQTT:** `{MQTT_BROKER}:{MQTT_PORT}`")
            st.write(f"**Topic Pattern:** `{WILDCARD_TOPIC}`")
            st.write(f"**API URL:** `{API_URL}`")
            st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        with st.expander("🔄 Opciones de Actualización", expanded=True):
            auto_refresh = st.checkbox("Auto-actualizar cada 10s", value=False)
            refresh_interval = st.slider("Intervalo de actualización (s)", 5, 60, 10)
            
            if auto_refresh:
                st.success("✓ Auto-actualización habilitada")
                import time
                time.sleep(refresh_interval)
                st.rerun()

        with st.expander("📅 Filtros Avanzados", expanded=False):
            st.write("**Configure los filtros globales:**")
            fecha_inicio = st.date_input("Fecha inicio", value=datetime.now() - timedelta(days=7))
            fecha_fin = st.date_input("Fecha fin", value=datetime.now())
            
            col1, col2 = st.columns(2)
            with col1:
                temp_min = st.number_input("Temp. mín (°C)", value=0.0)
                humedad_min = st.number_input("Humedad mín (%)", value=0.0)
            with col2:
                temp_max = st.number_input("Temp. máx (°C)", value=50.0)
                humedad_max = st.number_input("Humedad máx (%)", value=100.0)

    # Fetch zones
    zonas = obtener_zonas()

    if not zonas:
        st.warning("⚠️ No hay zonas disponibles")
        st.info("Los sensores deben estar publicando en topics: campo/tomate/sensores, campo/maiz/sensores, campo/zanahoria/sensores")
        return

    # Create tabs: one per zone + global
    tab_labels = [f"{ICONOS.get(z, '🌱')} {z.capitalize()}" for z in zonas]
    tab_labels.append("🌍 Análisis Global")

    tabs = st.tabs(tab_labels)

    # Individual zone tabs
    for idx, zona in enumerate(zonas):
        with tabs[idx]:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.title(f"{ICONOS.get(zona, '🌱')} {zona.capitalize()}")
            
            with col2:
                color_zona = COLORES.get(zona, "#999999")
                st.markdown(f"<div style='text-align:right; color:{color_zona}; font-size:20px;'>●</div>", unsafe_allow_html=True)
            
            with col3:
                st.metric("Estado", "Activo ✓")

            # Topic info
            st.markdown(f"**Topic MQTT:** `campo/{zona}/sensores` | **Wildcard:** `{WILDCARD_TOPIC}`")
            st.divider()

            # Fetch zone data
            datos = obtener_logs(zona)

            if datos:
                # Apply filters if specified
                df = pd.DataFrame(datos)
                df_filtrada = aplica_filtros(
                    df, 
                    pd.to_datetime(fecha_inicio),
                    pd.to_datetime(fecha_fin) + timedelta(days=1),
                    temp_min, temp_max, humedad_min, humedad_max
                )
                
                if len(df_filtrada) > 0:
                    # Metrics
                    st.subheader("📊 Métricas Estadísticas")
                    mostrar_metricas(zona, df_filtrada.to_dict('records'))

                    st.divider()

                    # Graphs
                    st.subheader("📈 Visualizaciones Detalladas")
                    mostrar_grafico_zona(zona, df_filtrada.to_dict('records'))

                    st.divider()

                    # Table
                    mostrar_tabla(zona, df_filtrada.to_dict('records'))
                else:
                    st.warning(f"⚠️ Sin datos que coincidan con los filtros seleccionados")
            else:
                st.info(f"Sin datos disponibles para: {zona}")

    # Global analysis tab
    with tabs[-1]:
        st.title("🌍 Análisis Global")

        # Fetch all data
        todos_datos = obtener_logs()

        if todos_datos:
            df_todos = pd.DataFrame(todos_datos)
            df_todos_filtrada = aplica_filtros(
                df_todos,
                pd.to_datetime(fecha_inicio),
                pd.to_datetime(fecha_fin) + timedelta(days=1),
                temp_min, temp_max, humedad_min, humedad_max
            )

            if len(df_todos_filtrada) > 0:
                # Global metrics
                st.subheader("📊 Métricas Globales")
                
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                
                temp_prom_global = df_todos_filtrada["temperatura"].mean()
                humedad_prom_global = df_todos_filtrada["humedad"].mean()
                cantidad_total = len(df_todos_filtrada)
                num_sensores = df_todos_filtrada["sensor_id"].nunique()
                
                with col1:
                    st.metric("🌡️ Temp. Prom.", f"{temp_prom_global:.1f}°C")
                with col2:
                    st.metric("💧 Humedad Prom.", f"{humedad_prom_global:.1f}%")
                with col3:
                    st.metric("📊 Total Lecturas", f"{cantidad_total}")
                with col4:
                    st.metric("🔌 Sensores Activos", f"{num_sensores}")
                with col5:
                    st.metric("🌱 Cultivos", f"{df_todos_filtrada['zona'].nunique()}")
                with col6:
                    st.metric("📡 QoS Promedio", "1")

                st.divider()

                # Comparative analysis
                st.subheader("📈 Análisis Comparativo")
                
                tab_comp1, tab_comp2, tab_comp3 = st.tabs(["📊 Comparativa Temporal", "🔄 Promedios por Zona", "⚡ Estadísticas Generales"])
                
                with tab_comp1:
                    # Comparative graph by zone
                    if "timestamp" in df_todos_filtrada.columns:
                        df_todos_filtrada["timestamp"] = pd.to_datetime(df_todos_filtrada["timestamp"])

                    fig_comp = go.Figure()
                    for zona in zonas:
                        df_zona = df_todos_filtrada[df_todos_filtrada["zona"] == zona].sort_values("timestamp")
                        if len(df_zona) > 0:
                            fig_comp.add_trace(go.Scatter(
                                x=df_zona["timestamp"],
                                y=df_zona["temperatura"],
                                mode="lines+markers",
                                name=f"{ICONOS.get(zona, '🌱')} {zona.capitalize()}",
                                line=dict(color=COLORES.get(zona, "#999999"), width=3),
                                marker=dict(size=6)
                            ))

                    fig_comp.update_layout(
                        title="Evolución de Temperaturas por Cultivo",
                        xaxis_title="Tiempo",
                        yaxis_title="Temperatura (°C)",
                        hovermode="x unified",
                        height=450,
                        template="plotly_white"
                    )
                    st.plotly_chart(fig_comp, use_container_width=True)
                
                with tab_comp2:
                    # Bar chart with average metrics by zone
                    df_promedio_zona = df_todos_filtrada.groupby("zona")[["temperatura", "humedad"]].mean().reset_index()
                    
                    fig_bar = go.Figure()
                    
                    fig_bar.add_trace(go.Bar(
                        x=df_promedio_zona["zona"],
                        y=df_promedio_zona["temperatura"],
                        name="Temperatura (°C)",
                        marker_color=[COLORES.get(z, "#999999") for z in df_promedio_zona["zona"]]
                    ))
                    
                    fig_bar.update_layout(
                        title="Temperatura Promedio por Cultivo",
                        xaxis_title="Cultivo",
                        yaxis_title="Temperatura (°C)",
                        height=400,
                        template="plotly_white"
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                    
                    # Humidity bar chart
                    fig_bar2 = go.Figure()
                    
                    fig_bar2.add_trace(go.Bar(
                        x=df_promedio_zona["zona"],
                        y=df_promedio_zona["humedad"],
                        name="Humedad (%)",
                        marker_color="#0099ff"
                    ))
                    
                    fig_bar2.update_layout(
                        title="Humedad Promedio por Cultivo",
                        xaxis_title="Cultivo",
                        yaxis_title="Humedad (%)",
                        height=400,
                        template="plotly_white"
                    )
                    st.plotly_chart(fig_bar2, use_container_width=True)
                
                with tab_comp3:
                    # Summary statistics
                    st.write("**Estadísticas Generales:**")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Temperatura (°C):**")
                        temp_stats = df_todos_filtrada["temperatura"].describe()
                        st.dataframe(temp_stats.round(2))
                    
                    with col2:
                        st.write("**Humedad (%):**")
                        humedad_stats = df_todos_filtrada["humedad"].describe()
                        st.dataframe(humedad_stats.round(2))

                st.divider()

                # Data table for all zones
                st.subheader("📋 Datos Completos")
                columnas = ["sensor_id", "zona", "temperatura", "humedad", "timestamp", "topic", "qos"]
                df_mostrar_todos = df_todos_filtrada[[col for col in columnas if col in df_todos_filtrada.columns]].head(50)
                
                if "timestamp" in df_mostrar_todos.columns:
                    df_mostrar_todos = df_mostrar_todos.copy()
                    df_mostrar_todos["timestamp"] = pd.to_datetime(df_mostrar_todos["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
                
                st.dataframe(
                    df_mostrar_todos,
                    use_container_width=True,
                    height=500,
                    column_config={
                        "temperatura": st.column_config.NumberColumn(format="%.2f °C"),
                        "humedad": st.column_config.NumberColumn(format="%.2f %%"),
                        "qos": st.column_config.NumberColumn(format="%d")
                    }
                )
            else:
                st.warning(f"⚠️ Sin datos que coincidan con los filtros seleccionados")
        else:
            st.info("Sin datos disponibles")


if __name__ == "__main__":
    main()
