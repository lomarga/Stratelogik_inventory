import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import norm

# 1. Configuración de la página (Layout amplio y título)
st.set_page_config(page_title="Stratelogik - Agente IA", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# 2. Inyección de CSS (Alto contraste, sidebar oscura, números blancos y detalles verdes)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
    }
    
    /* Fondo oscuro corporativo global y sidebar unificada */
    .stApp, [data-testid="stSidebar"] {
        background-color: #0E1117 !important;
    }

    /* Estilización de las tarjetas de KPI (Métricas) */
    div[data-testid="metric-container"] {
        background-color: #1E2127;
        border-left: 5px solid #00E676; /* Verde brillante */
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.5);
    }

    /* Forzar los números de las métricas a BLANCO PURO y muy gruesos */
    div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }
    
    /* Títulos de las tarjetas de métricas claros y legibles */
    div[data-testid="stMetricLabel"] p {
        color: #E2E8F0 !important;
        font-weight: 600 !important;
        font-size: 1.15rem !important;
    }

    /* Títulos y textos globales a blanco */
    h1, h2, h3, p, label, .stMarkdown {
        color: #FFFFFF !important;
    }
    
    /* Color principal de la marca (Texto verde) */
    .brand-text {
        color: #00E676 !important;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

# Diccionario de Z-scores para niveles de servicio
z_scores = {
    "90.0%": norm.ppf(0.90),
    "95.0%": norm.ppf(0.95),
    "98.0%": norm.ppf(0.98),
    "99.0%": norm.ppf(0.99),
    "99.9%": norm.ppf(0.999)
}

# 3. Panel Lateral con Logo y Entradas
with st.sidebar:
    try:
        st.image("logo_stratelogik.png", use_container_width=True)
    except FileNotFoundError:
        st.warning("⚠️ Guarda tu logo como 'logo_stratelogik.png' en esta carpeta.")
    
    st.markdown("---")
    st.header("Parámetros Operativos")
    demanda_media = st.slider("Demanda Media Diaria (uds)", min_value=500, max_value=5000, value=1500, step=100)
    volatilidad = st.slider("Volatilidad de la Demanda (%)", min_value=5, max_value=100, value=25, step=5)
    lead_time = st.slider("Tiempo de Entrega (Días)", min_value=1, max_value=20, value=5, step=1)
    nivel_servicio = st.selectbox("Nivel de Servicio Objetivo", options=list(z_scores.keys()), index=3)
    
    st.markdown("---")
    st.header("Parámetros Financieros")
    # Nuevo parámetro dinámico para el costo
    precio_unitario = st.number_input("Costo por Unidad (€)", min_value=0.1, max_value=5000.0, value=12.0, step=1.0)

# Cabecera Principal
st.markdown("<h1>🤖 Agente de Optimización de Inventarios <span class='brand-text'>Stratelogik</span></h1>", unsafe_allow_html=True)
st.markdown("Cálculo dinámico del Punto de Reorden (ROP) y prevención de quiebres de stock en entornos de alta volatilidad.")
st.markdown("---")

# Cálculos del Agente
z = z_scores[nivel_servicio]
desviacion_demanda = demanda_media * (volatilidad / 100)
stock_seguridad = int(z * desviacion_demanda * np.sqrt(lead_time))
demanda_lead_time = demanda_media * lead_time
rop = int(demanda_lead_time + stock_seguridad)
cantidad_pedido = demanda_media * 10 # Política de pedir para 10 días

# Mostrar KPIs (El capital se calcula ahora usando el precio_unitario dinámico)
col1, col2, col3 = st.columns(3)
col1.metric("Stock de Seguridad Sugerido", f"{stock_seguridad:,} uds")
col2.metric("Punto de Reorden Óptimo (ROP)", f"{rop:,} uds", delta="Alerta Activa", delta_color="off")
col3.metric("Capital Inmovilizado (Riesgo)", f"€ {stock_seguridad * precio_unitario:,.2f}", help=f"Cálculo: Stock de Seguridad x {precio_unitario} €")

st.markdown("<br>", unsafe_allow_html=True)

# Simulación extendida a 90 días para el gráfico
dias = 90
inventario = [rop + cantidad_pedido] # Inventario inicial alto
en_transito = []

np.random.seed(42) # Semilla fija para mantener la curva base
historial_demanda = np.random.normal(demanda_media, desviacion_demanda, dias).astype(int)

for dia in range(1, dias):
    # Procesar llegadas de pedidos
    llegadas = [pedido['cantidad'] for pedido in en_transito if pedido['dia_llegada'] == dia]
    inv_actual = inventario[-1] + sum(llegadas) - historial_demanda[dia]
    
    inv_actual = max(0, inv_actual) # Prevenir números negativos
    inventario.append(inv_actual)
    
    # Decisión de pedir
    if inv_actual <= rop and not any(p['dia_llegada'] > dia for p in en_transito):
        en_transito.append({'cantidad': cantidad_pedido, 'dia_llegada': dia + lead_time})

# 4. Gráfico con Plotly adaptado al tema de alto contraste (Horizonte de 90 días)
dias_x = list(range(dias))
fig = go.Figure()

# Área del Stock de Seguridad (Gris/Rojo para riesgo)
fig.add_trace(go.Scatter(
    x=dias_x, y=[stock_seguridad]*dias, fill='tozeroy', mode='none',
    fillcolor='rgba(239, 68, 68, 0.2)', name='Stock de Seguridad Crítico'
))

# Línea del ROP (Verde Stratelogik)
fig.add_trace(go.Scatter(
    x=dias_x, y=[rop]*dias, mode='lines', line=dict(color='#00E676', width=3, dash='dash'),
    name='Punto de Reorden (ROP)'
))

# Evolución del Inventario (Blanco)
fig.add_trace(go.Scatter(
    x=dias_x, y=inventario, mode='lines+markers', line=dict(color='#FFFFFF', width=3),
    marker=dict(size=6, color='#00E676', line=dict(width=1, color='#FFFFFF')), name='Nivel de Inventario Simulado'
))

fig.update_layout(
    title=dict(text="Comportamiento del Inventario vs ROP Inteligente (Ciclo de 90 días)", font=dict(color='#FFFFFF')),
    xaxis=dict(title="Días de Operación", color='#FFFFFF', gridcolor='#2D3748'),
    yaxis=dict(title="Unidades en Almacén", color='#FFFFFF', gridcolor='#2D3748'),
    template="plotly_dark",
    plot_bgcolor="#0E1117",
    paper_bgcolor="#0E1117",
    hovermode="x unified",
    margin=dict(l=20, r=20, t=50, b=20),
    legend=dict(font=dict(color='#FFFFFF'), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)