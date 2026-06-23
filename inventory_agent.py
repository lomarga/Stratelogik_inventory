import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scipy.stats import norm
import datetime

# 1. Configuración de la página
st.set_page_config(page_title="Stratelogik - Optimización de Inventarios", layout="wide", initial_sidebar_state="expanded")

# 2. Inyección de CSS (UI Premium, Pestañas Oscuras de Alto Contraste)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; }
    .stApp, [data-testid="stSidebar"] { background-color: #0A192F !important; }
    
    div[data-testid="metric-container"] {
        background-color: #112240; border-left: 5px solid #00D2FF; 
        padding: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.5);
    }
    div[data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: 800 !important; }
    div[data-testid="stMetricLabel"] p { color: #E2E8F0 !important; font-weight: 600 !important; font-size: 1.15rem !important; }
    h1, h2, h3, h4, p, label, .stMarkdown { color: #FFFFFF !important; }
    .brand-text { color: #00D2FF !important; font-weight: 800; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; border-bottom: 1px solid #1C2541; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; white-space: pre-wrap; background-color: #112240; 
        border-radius: 6px 6px 0 0; color: #8892B0 !important; font-weight: 600; 
        border: 1px solid #1C2541; border-bottom: none; margin-bottom: -1px;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #162C4E !important; 
        color: #FFFFFF !important; 
        border-bottom: 3px solid #00D2FF !important; 
        box-shadow: 0 -4px 10px rgba(0, 210, 255, 0.05);
    }
    
    .control-box { background-color: #112240; padding: 20px; border-radius: 8px; border: 1px solid #1C2541; margin-bottom: 20px; }
    .instrucciones-box { background-color: #112240; padding: 30px; border-radius: 8px; border: 1px solid #1C2541; margin-top: 20px;}
    .sku-badge { background-color: #00D2FF; color: #0A192F; padding: 4px 12px; border-radius: 20px; font-weight: 800; font-size: 0.9rem; margin-left: 15px;}
    
    .matrix-grid { display: grid; grid-template-columns: 120px 1fr 1fr 1fr; gap: 8px; margin-bottom: 30px; }
    .m-header-top { padding: 15px; text-align: center; border-radius: 6px; }
    .m-header-top.x { background-color: #1B5E20; }
    .m-header-top.y { background-color: #F57F17; }
    .m-header-top.z { background-color: #B71C1C; }
    .m-header-left { padding: 15px; text-align: center; border-radius: 6px; display: flex; align-items: center; justify-content: center; background-color: #0D47A1; }
    .m-cell { background-color: #112240; padding: 15px; border-radius: 6px; border-top: 4px solid; }
    .m-cell.ax, .m-cell.bx, .m-cell.cx { border-top-color: #00E676; }
    .m-cell.ay, .m-cell.by, .m-cell.cy { border-top-color: #FFD600; }
    .m-cell.az, .m-cell.bz, .m-cell.cz { border-top-color: #FF5252; }
    .m-title { font-size: 1.1rem; font-weight: 800; margin-bottom: 5px; }
    .m-subtitle { font-size: 0.85rem; font-weight: 600; margin-bottom: 10px; }
    .m-text { font-size: 0.85rem; color: #E2E8F0; line-height: 1.4; margin-bottom: 8px; }
    
    .summary-box { background-color: #162C4E; border-radius: 8px; padding: 15px; text-align: center; border: 1px solid #1C2541; }
    .summary-val { font-size: 2rem; font-weight: 800; color: #00D2FF; }
    .summary-label { font-size: 0.9rem; color: #E2E8F0; font-weight: 600; }
    
    .glossary-card { background-color: #112240; padding: 25px; border-radius: 8px; border-left: 4px solid #00D2FF; margin-bottom: 15px; }
    .glossary-title { font-size: 1.2rem; font-weight: 800; color: #00D2FF; margin-bottom: 8px; }
    .glossary-desc { font-size: 1rem; color: #E2E8F0; line-height: 1.5; }
    </style>
    """, unsafe_allow_html=True)

def fmt_entero(val): return f"{int(val):,}".replace(",", ".")
def fmt_decimal(val): return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

@st.cache_data
def generar_plantilla_transaccional():
    dias_historia = 60
    fechas_base = pd.date_range(end=datetime.date.today(), periods=dias_historia)
    perfiles_sku = [
        ('SKU-A100', 5000, 150, 60000), ('SKU-B200', 4500, 2500, 80000),
        ('SKU-C300', 150, 120, 2000), ('SKU-D400', 200, 10, 2500),
        ('SKU-E500', 1500, 80, 18000), ('SKU-F600', 1200, 800, 25000),
        ('SKU-G700', 8000, 1200, 100000), ('SKU-H800', 50, 80, 600),
        ('SKU-I900', 3000, 400, 35000), ('SKU-J000', 600, 30, 8000)
    ]
    np.random.seed(42)
    data_rows = []
    for sku, media, std, inv_actual in perfiles_sku:
        for f in fechas_base:
            dem = int(max(0, np.random.normal(media, std)))
            inv_actual -= dem
            if inv_actual < (media * 3): inv_actual += int(media * 12)
            data_rows.append({'Fecha': f.strftime('%d-%m-%Y'), 'SKU': sku, 'Demanda_Diaria': dem, 'Inventario_Final': inv_actual})
    df_template = pd.DataFrame(data_rows)
    return df_template.to_csv(index=False).encode('utf-8')

z_scores = { "90.0%": norm.ppf(0.90), "95.0%": norm.ppf(0.95), "98.0%": norm.ppf(0.98), "99.0%": norm.ppf(0.99), "99.9%": norm.ppf(0.999) }

with st.sidebar:
    try: st.image("logo_stratelogik.png", use_container_width=True)
    except FileNotFoundError: st.warning("Archivo de imagen corporativa no detectado.")
    
    st.markdown("---")
    st.subheader("Base de Datos Operativa")
    st.download_button("Descargar Plantilla Base", data=generar_plantilla_transaccional(), file_name='historial_operativo.csv', mime='text/csv')
    archivo_csv = st.file_uploader("Cargar historial de movimientos", type=["csv"])

st.markdown("<h1>Sistema de Inteligencia y Optimización de Inventarios <span class='brand-text'>Stratelogik</span></h1>", unsafe_allow_html=True)

if archivo_csv is None:
    st.markdown("""
    <div class="instrucciones-box">
        <h3>Inicialización de la Plataforma</h3>
        <p style="margin-top: 15px; font-size: 1.1rem; color: #8892B0 !important;">
            El motor de análisis requiere la carga de datos históricos para habilitar los modelos predictivos y de segmentación.
        </p>
        <ol style="color: #E2E8F0; font-size: 1.1rem; line-height: 1.8; margin-top: 10px;">
            <li>Obtenga la estructura base (CSV) mediante el panel lateral.</li>
            <li>Incorpore los registros diarios de demanda y stock final.</li>
            <li>Cargue el archivo para activar los dashboards tácticos.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

else:
    df_global = pd.read_csv(archivo_csv)
    df_global['Fecha'] = pd.to_datetime(df_global['Fecha'], format='%d-%m-%Y')
    df_global = df_global.sort_values('Fecha')
    sku_list = df_global['SKU'].unique().tolist()

    tab1, tab2, tab3 = st.tabs(["Segmentación ABC-XYZ", "Simulación de Escenarios y Alertas", "Glosario de Términos"])

    # --- TAB 1: SEGMENTACIÓN ABC-XYZ ---
    with tab1:
        st.markdown("""
            <div style='background-color: #112240; padding: 15px; border-left: 4px solid #00D2FF; border-radius: 4px; margin-bottom: 20px;'>
                <p style='margin: 0; color: #E2E8F0; font-size: 1.05rem;'>
                    <b>Objetivo de esta vista:</b> Segmentar el portafolio en 9 cuadrantes estratégicos cruzando el volumen de ventas (Pareto ABC) con la volatilidad de la demanda (Clase XYZ). Esta clasificación permite enfocar el esfuerzo operativo en los artículos más críticos y estandarizar políticas de compra por grupo.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="control-box">', unsafe_allow_html=True)
        st.subheader("Parámetros de Clasificación de Portafolio")
        
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        with col_p1: p_a = st.slider("Frontera Clase A (Pareto %)", 50, 90, 80, 5)
        with col_p2: p_b = st.slider("Frontera Clase B (Pareto %)", p_a + 5, 99, 95, 1)
        with col_p3: x_max = st.number_input("Límite Clase X (CV Máximo)", 0.05, 0.50, 0.20, 0.05)
        with col_p4: y_max = st.number_input("Límite Clase Y (CV Máximo)", x_max + 0.1, 1.5, 0.7, 0.1)
        st.markdown('</div>', unsafe_allow_html=True)

        df_r = df_global.groupby('SKU')['Demanda_Diaria'].agg(['sum', 'mean', 'std']).reset_index()
        df_r.rename(columns={'sum': 'D_Total', 'mean': 'D_Media', 'std': 'Std'}, inplace=True)
        df_r['CV'] = np.where(df_r['D_Media'] > 0, df_r['Std'] / df_r['D_Media'], 0)
        df_r = df_r.sort_values(by='D_Total', ascending=False)
        
        df_r['Acc'] = df_r['D_Total'].cumsum() / df_r['D_Total'].sum()
        df_r['Acc_Pct'] = df_r['Acc'] * 100 
        
        df_r['ABC'] = df_r['Acc'].apply(lambda x: 'A' if x <= p_a/100 else ('B' if x <= p_b/100 else 'C'))
        df_r['XYZ'] = df_r['CV'].apply(lambda x: 'X' if x <= x_max else ('Y' if x <= y_max else 'Z'))
        df_r['Cat'] = df_r['ABC'] + df_r['XYZ']

        max_y_val = max(df_r['CV'].max(), y_max) * 1.15

        fig_sc = px.scatter(
            df_r, x="Acc_Pct", y="CV", color="Cat", hover_name="SKU",
            labels={"Acc_Pct": "Participación Acumulada de Demanda (%)", "CV": "Coeficiente de Variación (CV)"},
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        
        fig_sc.add_shape(type="rect", x0=0, y0=0, x1=p_a, y1=x_max, fillcolor="rgba(0, 230, 118, 0.08)", line_width=0, layer="below")
        fig_sc.add_shape(type="rect", x0=p_a, y0=0, x1=p_b, y1=x_max, fillcolor="rgba(0, 230, 118, 0.05)", line_width=0, layer="below")
        fig_sc.add_shape(type="rect", x0=p_b, y0=0, x1=105, y1=x_max, fillcolor="rgba(0, 230, 118, 0.02)", line_width=0, layer="below")
        fig_sc.add_shape(type="rect", x0=0, y0=x_max, x1=p_a, y1=y_max, fillcolor="rgba(255, 214, 0, 0.08)", line_width=0, layer="below")
        fig_sc.add_shape(type="rect", x0=p_a, y0=x_max, x1=p_b, y1=y_max, fillcolor="rgba(255, 214, 0, 0.05)", line_width=0, layer="below")
        fig_sc.add_shape(type="rect", x0=p_b, y0=x_max, x1=105, y1=y_max, fillcolor="rgba(255, 214, 0, 0.02)", line_width=0, layer="below")
        fig_sc.add_shape(type="rect", x0=0, y0=y_max, x1=p_a, y1=max_y_val, fillcolor="rgba(255, 82, 82, 0.08)", line_width=0, layer="below")
        fig_sc.add_shape(type="rect", x0=p_a, y0=y_max, x1=p_b, y1=max_y_val, fillcolor="rgba(255, 82, 82, 0.05)", line_width=0, layer="below")
        fig_sc.add_shape(type="rect", x0=p_b, y0=y_max, x1=105, y1=max_y_val, fillcolor="rgba(255, 82, 82, 0.02)", line_width=0, layer="below")

        fig_sc.add_vline(x=p_a, line_width=2, line_dash="dash", line_color="#8892B0", annotation_text="A | B", annotation_position="top left", annotation_font_color="#FFFFFF")
        fig_sc.add_vline(x=p_b, line_width=2, line_dash="dash", line_color="#8892B0", annotation_text="B | C", annotation_position="top left", annotation_font_color="#FFFFFF")
        fig_sc.add_hline(y=x_max, line_width=2, line_dash="dash", line_color="#8892B0", annotation_text="X | Y", annotation_font_color="#FFFFFF")
        fig_sc.add_hline(y=y_max, line_width=2, line_dash="dash", line_color="#8892B0", annotation_text="Y | Z", annotation_font_color="#FFFFFF")
        
        fig_sc.update_layout(
            title=dict(text="Dispersión ABC vs XYZ — Ranking por Valor (Eje X) • Coeficiente de Variación (Eje Y)", font=dict(color='#FFFFFF', size=16)),
            xaxis=dict(color='#FFFFFF', gridcolor='#1C2541', range=[0, 105]),
            yaxis=dict(color='#FFFFFF', gridcolor='#1C2541', range=[0, max_y_val]),
            template="plotly_dark", plot_bgcolor="#0A192F", paper_bgcolor="#0A192F", height=600, margin=dict(t=50, b=40, l=40, r=40)
        )
        st.plotly_chart(fig_sc, use_container_width=True)

        st.markdown("### Distribución del Portafolio")
        resumen_cat = df_r['Cat'].value_counts().to_dict()
        for c in ['AX','AY','AZ','BX','BY','BZ','CX','CY','CZ']:
            if c not in resumen_cat: resumen_cat[c] = 0
            
        c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(9)
        cats = ['AX','AY','AZ','BX','BY','BZ','CX','CY','CZ']
        cols = [c1, c2, c3, c4, c5, c6, c7, c8, c9]
        for col, cat in zip(cols, cats):
            with col:
                st.markdown(f'<div class="summary-box"><div class="summary-val">{resumen_cat[cat]}</div><div class="summary-label">{cat}</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        html_matriz = """<div class="matrix-grid">
<div style="background:transparent;"></div>
<div class="m-header-top x"><b>X - Estable</b><br>CV ≤ {X_MAX}</div>
<div class="m-header-top y"><b>Y - Variable</b><br>{X_MAX} < CV ≤ {Y_MAX}</div>
<div class="m-header-top z"><b>Z - Impredecible</b><br>CV > {Y_MAX}</div>
<div class="m-header-left"><b>A<br>Alto Valor</b></div>
<div class="m-cell ax">
<div class="m-title" style="color:#00E676;">AX</div>
<div class="m-subtitle" style="color:#00E676;">Alta prioridad, bajo riesgo</div>
<div class="m-text"><b>Riesgo:</b> Demanda estable, pero la rotura de stock es muy costosa.</div>
<div class="m-text"><b>Estrategia:</b> Control estricto, revisión frecuente y reposición Lean.</div>
<div class="m-text"><b>Política:</b> Bajo stock de seguridad, ROP fijo automático.</div>
</div>
<div class="m-cell ay">
<div class="m-title" style="color:#FFD600;">AY</div>
<div class="m-subtitle" style="color:#FFD600;">Alta prioridad, riesgo moderado</div>
<div class="m-text"><b>Riesgo:</b> El alto valor más la demanda variable crean riesgo de rotura y sobrestock.</div>
<div class="m-text"><b>Estrategia:</b> Pronóstico activo (S&OP) y revisión regular.</div>
<div class="m-text"><b>Política:</b> Buffer moderado, cadencia de reposición ajustada.</div>
</div>
<div class="m-cell az">
<div class="m-title" style="color:#FF5252;">AZ</div>
<div class="m-subtitle" style="color:#FF5252;">Crítico, máximo riesgo</div>
<div class="m-text"><b>Riesgo:</b> Costosos e impredecibles. Cada rotura duele.</div>
<div class="m-text"><b>Estrategia:</b> Proteger disponibilidad con stock extra o envíos rápidos.</div>
<div class="m-text"><b>Política:</b> Gran buffer, revisión semanal, cobertura premium.</div>
</div>
<div class="m-header-left"><b>B<br>Valor Medio</b></div>
<div class="m-cell bx">
<div class="m-title" style="color:#00E676;">BX</div>
<div class="m-subtitle" style="color:#00E676;">Prioridad estándar</div>
<div class="m-text"><b>Riesgo:</b> Categoría manejable con reglas estándar.</div>
<div class="m-text"><b>Estrategia:</b> Aplicar reposición rutinaria.</div>
<div class="m-text"><b>Política:</b> Stock de seguridad moderado, revisión periódica.</div>
</div>
<div class="m-cell by">
<div class="m-title" style="color:#FFD600;">BY</div>
<div class="m-subtitle" style="color:#FFD600;">Vigilancia constante</div>
<div class="m-text"><b>Riesgo:</b> La variabilidad puede erosionar el nivel de servicio.</div>
<div class="m-text"><b>Estrategia:</b> Revisar buffers ante cambios de tendencia.</div>
<div class="m-text"><b>Política:</b> Reglas Min-Max o revisión periódica.</div>
</div>
<div class="m-cell bz">
<div class="m-title" style="color:#FF5252;">BZ</div>
<div class="m-subtitle" style="color:#FF5252;">Monitoreo activo</div>
<div class="m-text"><b>Riesgo:</b> El esfuerzo de planificación es alto respecto a su valor.</div>
<div class="m-text"><b>Estrategia:</b> Favorecer reposición reactiva o Make-to-Order.</div>
<div class="m-text"><b>Política:</b> Buffer práctico solo si es necesario, simplificar.</div>
</div>
<div class="m-header-left"><b>C<br>Bajo Valor</b></div>
<div class="m-cell cx">
<div class="m-title" style="color:#00E676;">CX</div>
<div class="m-subtitle" style="color:#00E676;">Baja prioridad</div>
<div class="m-text"><b>Riesgo:</b> Costo de gestión superior al valor del producto.</div>
<div class="m-text"><b>Estrategia:</b> Minimizar tiempo de atención (Touch time).</div>
<div class="m-text"><b>Política:</b> Compras por lotes grandes (Bulk), reposición visual.</div>
</div>
<div class="m-cell cy">
<div class="m-title" style="color:#FFD600;">CY</div>
<div class="m-subtitle" style="color:#FFD600;">Baja prioridad, riesgo stock muerto</div>
<div class="m-text"><b>Riesgo:</b> Acumulación de inventario obsoleto.</div>
<div class="m-text"><b>Estrategia:</b> Consolidar compras.</div>
<div class="m-text"><b>Política:</b> Sin stock de seguridad salvo excepciones.</div>
</div>
<div class="m-cell cz">
<div class="m-title" style="color:#FF5252;">CZ</div>
<div class="m-subtitle" style="color:#FF5252;">Candidatos a eliminación</div>
<div class="m-text"><b>Riesgo:</b> Inventario inmovilizado sin movimiento.</div>
<div class="m-text"><b>Estrategia:</b> Eliminar del catálogo o gestionar estrictamente bajo pedido.</div>
<div class="m-text"><b>Política:</b> Cero stock (Make-to-Order).</div>
</div>
</div>""".replace("{X_MAX}", str(x_max)).replace("{Y_MAX}", str(y_max))

        st.markdown(html_matriz, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        df_mostrar = df_r[['SKU', 'Cat', 'D_Total', 'CV', 'ABC', 'XYZ']].copy()
        df_mostrar.columns = ['SKU', 'Categoría', 'Demanda Acumulada', 'Coef. Variación', 'Clase ABC', 'Clase XYZ']
        st.dataframe(df_mostrar.style.format({'Coef. Variación': '{:.1%}', 'Demanda Acumulada': '{:,.0f}'}), use_container_width=True)

    # --- TAB 2: SIMULACIÓN DE ESCENARIOS Y ALERTAS ---
    with tab2:
        st.markdown("""
            <div style='background-color: #112240; padding: 15px; border-left: 4px solid #00D2FF; border-radius: 4px; margin-bottom: 20px;'>
                <p style='margin: 0; color: #E2E8F0; font-size: 1.05rem;'>
                    <b>Objetivo de esta vista:</b> Ejecutar un modelo estocástico sobre un SKU específico para simular su comportamiento futuro. La plataforma calcula dinámicamente el Punto de Reorden (ROP), el Stock de Seguridad y el Nivel Máximo, previniendo tanto los quiebres de stock como la inmovilización innecesaria de capital.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="control-box">', unsafe_allow_html=True)
        st.subheader("Parámetros de Control Táctico")
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        with col_c1: lead_time = st.slider("Lead Time", 1, 45, 3, 1)
        with col_c2: dias_cobertura = st.slider("Lote de compra (días)", 1, 90, 10, 1)
        with col_c3: nivel_servicio = st.selectbox("Nivel Servicio", list(z_scores.keys()), index=3)
        with col_c4: precio_unitario = st.number_input("Costo Unit. (€)", 0.1, 10000.0, 12.0, 1.0)
        st.markdown('</div>', unsafe_allow_html=True)
        
        z = z_scores[nivel_servicio]

        st.markdown("---")
        st.subheader("Radiografía de Inventarios (Estado del Portafolio)")
        
        fechas_unicas = df_global['Fecha'].dt.strftime('%d-%m-%Y').unique()
        fecha_seleccionada = st.selectbox("Seleccione fecha de corte transversal para analizar el portafolio completo:", fechas_unicas, index=len(fechas_unicas)-1)
        fecha_filtro = pd.to_datetime(fecha_seleccionada, format='%d-%m-%Y')
        
        df_snap = df_global[df_global['Fecha'] == fecha_filtro].copy()
        df_stats = df_global.groupby('SKU')['Demanda_Diaria'].agg(['mean', 'std']).reset_index()
        df_snap = df_snap.merge(df_stats, on='SKU')
        
        df_snap['SS_calc'] = (z * df_snap['std'] * np.sqrt(lead_time)).fillna(0).astype(int)
        df_snap['ROP_calc'] = (df_snap['mean'] * lead_time).astype(int) + df_snap['SS_calc']
        df_snap['Max_calc'] = df_snap['ROP_calc'] + (df_snap['mean'] * dias_cobertura).astype(int)
        
        def determinar_estado(row):
            if row['Inventario_Final'] < row['SS_calc']: return "Crítico (< Stock Seg.)"
            elif row['Inventario_Final'] <= row['ROP_calc']: return "Zona de Compra"
            elif row['Inventario_Final'] <= row['Max_calc']: return "Saludable"
            else: return "Exceso (> Máx)"
            
        df_snap['Estado'] = df_snap.apply(determinar_estado, axis=1)
        
        color_map = {
            "Crítico (< Stock Seg.)": "#FF5252", 
            "Zona de Compra": "#FFD600", 
            "Saludable": "#00E676", 
            "Exceso (> Máx)": "#8892B0"
        }
        
        df_snap = df_snap.sort_values(by=['Estado', 'Inventario_Final'], ascending=[True, False])
        
        fig_health = px.bar(
            df_snap, x='SKU', y='Inventario_Final', color='Estado',
            color_discrete_map=color_map, labels={"Inventario_Final": "Unidades Físicas en Almacén"},
            hover_data={'Inventario_Final': True, 'ROP_calc': True, 'Max_calc': True, 'Estado': False}
        )
        
        fig_health.update_layout(
            title=dict(text=f"Nivel de Inventario vs Alertas por SKU (Fecha: {fecha_seleccionada})", font=dict(color='#FFFFFF', size=16)),
            xaxis=dict(title="Productos (SKU)", color='#FFFFFF', gridcolor='#1C2541'),
            yaxis=dict(title="Unidades Físicas", color='#FFFFFF', gridcolor='#1C2541'),
            template="plotly_dark", plot_bgcolor="#0A192F", paper_bgcolor="#0A192F", margin=dict(t=50, b=40, l=40, r=40)
        )
        st.plotly_chart(fig_health, use_container_width=True)

        st.markdown("---")
        st.subheader("Simulación Analítica por SKU")
        
        col_sku, col_blank = st.columns([1, 2])
        with col_sku:
            sku_seleccionado = st.selectbox("Seleccione el identificador (SKU) para evaluar la proyección:", sku_list, key='sku_simulador_box')
        
        cat_asignada = df_r.loc[df_r['SKU'] == sku_seleccionado, 'Cat'].values[0]
        st.markdown(f"<p style='font-size: 1.2rem; margin-bottom: 20px;'>Clasificación Estratégica actual del producto: <span class='sku-badge'>{cat_asignada}</span></p>", unsafe_allow_html=True)

        df_sku_completo = df_global[df_global['SKU'] == sku_seleccionado].copy()
        mean_demand = df_sku_completo['Demanda_Diaria'].mean()
        std_demand = df_sku_completo['Demanda_Diaria'].std()
        def_demanda, def_volatilidad = int(mean_demand), int((std_demand / mean_demand) * 100) if mean_demand > 0 else 0
        def_inv_actual = int(df_sku_completo.iloc[-1]['Inventario_Final'])
        ultima_fecha_hist = df_sku_completo.iloc[-1]['Fecha']

        placeholder_kpis = st.container()
        placeholder_chart = st.container()

        st.markdown('<div class="control-box">', unsafe_allow_html=True)
        st.subheader("Variables de Demanda Real Histórica (Modificables solo para demostración)")
        col_d1, col_d2 = st.columns(2)
        with col_d1: demanda_media = st.number_input("Demanda Media Diaria (unidades)", min_value=1, max_value=50000, value=def_demanda)
        with col_d2: volatilidad = st.number_input("Volatilidad de Demanda (CV %)", min_value=1, max_value=300, value=def_volatilidad)
        st.markdown('</div>', unsafe_allow_html=True)

        stock_seguridad = int(z * (demanda_media * (volatilidad / 100)) * np.sqrt(lead_time))
        rop = int((demanda_media * lead_time) + stock_seguridad)
        cantidad_pedido = demanda_media * dias_cobertura
        max_target = rop + cantidad_pedido

        with placeholder_kpis:
            col_k1, col_k2, col_k3, col_k4 = st.columns(4)
            col_k1.metric("Stock de Seguridad", f"{fmt_entero(stock_seguridad)} uds")
            col_k2.metric("Punto de Reorden (ROP)", f"{fmt_entero(rop)} uds")
            col_k3.metric("Nivel Máximo (Target)", f"{fmt_entero(max_target)} uds")
            col_k4.metric("Capital Inmovilizado", f"€ {fmt_decimal(stock_seguridad * precio_unitario)}")

        dias_sim = 90
        inv_f = [def_inv_actual]
        en_t = []
        np.random.seed(42)
        dem_f = np.maximum(0, np.random.normal(demanda_media, demanda_media*(volatilidad/100), dias_sim)).astype(int)
        fechas_f = pd.date_range(start=ultima_fecha_hist + pd.Timedelta(days=1), periods=dias_sim)

        for d in range(1, dias_sim):
            lleg = sum([p['q'] for p in en_t if p['d'] == d])
            inv_a = max(0, inv_f[-1] + lleg - dem_f[d])
            inv_f.append(inv_a)
            if inv_a <= rop and not any(p['d'] > d for p in en_t):
                en_t.append({'q': cantidad_pedido, 'd': d + lead_time})

        fig_sim = go.Figure()
        df_hp = df_sku_completo.tail(21)
        fig_sim.add_trace(go.Scatter(x=df_hp['Fecha'], y=df_hp['Inventario_Final'], mode='lines+markers', line=dict(color='#8892B0', width=3), name='Historial'))
        fig_sim.add_trace(go.Scatter(x=[df_hp.iloc[-1]['Fecha'], fechas_f[0]], y=[df_hp.iloc[-1]['Inventario_Final'], inv_f[0]], mode='lines', line=dict(color='#FFFFFF', width=2, dash='dot'), showlegend=False))
        fig_sim.add_trace(go.Scatter(x=fechas_f, y=[stock_seguridad]*dias_sim, fill='tozeroy', mode='none', fillcolor='rgba(239, 68, 68, 0.15)', name='Stock Seguridad'))
        fig_sim.add_trace(go.Scatter(x=fechas_f, y=[rop]*dias_sim, mode='lines', line=dict(color='#00D2FF', width=3, dash='dash'), name='ROP IA'))
        fig_sim.add_trace(go.Scatter(x=fechas_f, y=[max_target]*dias_sim, mode='lines', line=dict(color='#8892B0', width=2, dash='dot'), name='Nivel Máximo'))
        fig_sim.add_trace(go.Scatter(x=fechas_f, y=inv_f, mode='lines', line=dict(color='#FFFFFF', width=3), name='Proyección'))
        
        fig_sim.add_vline(x=ultima_fecha_hist, line_width=2, line_dash="dash", line_color="#00D2FF")
        fig_sim.update_layout(template="plotly_dark", plot_bgcolor="#0A192F", paper_bgcolor="#0A192F", margin=dict(t=50, b=20))
        
        with placeholder_chart:
            st.plotly_chart(fig_sim, use_container_width=True)

    # --- TAB 3: GLOSARIO DE TÉRMINOS ---
    with tab3:
        st.markdown("""
            <div style='background-color: #112240; padding: 15px; border-left: 4px solid #00D2FF; border-radius: 4px; margin-bottom: 20px;'>
                <p style='margin: 0; color: #E2E8F0; font-size: 1.05rem;'>
                    <b>Objetivo de esta vista:</b> Proveer un diccionario analítico estandarizado. Define los conceptos estadísticos y operativos clave que el motor de simulación utiliza para generar las recomendaciones tácticas.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="glossary-card">
            <div class="glossary-title">Clasificación ABC (Análisis de Pareto)</div>
            <div class="glossary-desc">
                Metodología de segmentación basada en el principio de que un pequeño porcentaje de productos representa la mayor parte del volumen físico o valor financiero. La Clase A engloba los SKU principales (hasta el 80% acumulado), la Clase B el volumen intermedio (hasta el 95%) y la Clase C los artículos de baja rotación.
            </div>
        </div>
        
        <div class="glossary-card">
            <div class="glossary-title">Clasificación XYZ (Coeficiente de Variación)</div>
            <div class="glossary-desc">
                Segmentación que evalúa la predictibilidad de la demanda analizando su dispersión estadística en el tiempo. Los artículos X presentan flujos constantes (CV bajo); los artículos Y muestran fluctuaciones moderadas; y los artículos Z corresponden a demandas altamente erráticas o impredecibles.
            </div>
        </div>
        
        <div class="glossary-card">
            <div class="glossary-title">Coeficiente de Variación (CV)</div>
            <div class="glossary-desc">
                Indicador estadístico estandarizado que mide la relación entre la desviación estándar y la media de la demanda. Permite comparar de forma justa la estabilidad o inestabilidad operativa entre productos que tienen volúmenes de venta muy diferentes.
            </div>
        </div>
        
        <div class="glossary-card">
            <div class="glossary-title">Nivel de Servicio Objetivo (Service Level)</div>
            <div class="glossary-desc">
                Métrica estratégica que representa la probabilidad estadística de satisfacer la demanda de los clientes sin incurrir en roturas de stock o desabastecimientos durante un ciclo de reabastecimiento. Un mayor nivel de servicio requerido (por ejemplo, 98% o 99%) reduce drásticamente el riesgo comercial, pero exige dimensionar un Stock de Seguridad significativamente más robusto, incrementando el capital de cobertura retenido en el almacén.
            </div>
        </div>
        
        <div class="glossary-card">
            <div class="glossary-title">Punto de Reorden (ROP - Reorder Point)</div>
            <div class="glossary-desc">
                Nivel crítico de existencias que actúa como disparador logístico. Cuando el inventario físico cae por debajo de este umbral, el sistema emite automáticamente una orden de compra para asegurar que el reabastecimiento llegue antes de tener que tocar el Stock de Seguridad.
            </div>
        </div>
        
        <div class="glossary-card">
            <div class="glossary-title">Stock de Seguridad (Safety Stock)</div>
            <div class="glossary-desc">
                Inventario de protección diseñado para mitigar los riesgos derivados de picos inesperados en la demanda del mercado o retrasos en los tiempos de entrega del proveedor. Su volumen aumenta a medida que aumenta la volatilidad del producto y el Nivel de Servicio que la empresa desea garantizar.
            </div>
        </div>
        
        <div class="glossary-card">
            <div class="glossary-title">Lote de Compra (Días de Cobertura)</div>
            <div class="glossary-desc">
                Parámetro táctico que define el tamaño del pedido de reabastecimiento, expresado en la cantidad de días de consumo promedio que debe cubrir. Un lote alto mejora los costos de flete, pero incrementa dramáticamente el capital inmovilizado en la bodega.
            </div>
        </div>
        
        <div class="glossary-card">
            <div class="glossary-title">Nivel Máximo (Target Stock)</div>
            <div class="glossary-desc">
                Techo teórico ideal de inventario. Representa la capacidad máxima que alcanzará el almacén justo en el instante en que ingresa el pedido completo del proveedor. Cualquier volumen sostenido por encima de esta línea evidencia una ineficiencia en la compra (sobrestock).
            </div>
        </div>
        """, unsafe_allow_html=True)