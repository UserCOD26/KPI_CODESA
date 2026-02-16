import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Tableros Corporativos CODESA", layout="wide", page_icon="🏢")

# ==========================================
# 🧠 CÁLCULO INTELIGENTE DE AÑOS
# ==========================================
anio_actual = datetime.now().year
anio_inicio = 2026
ANIOS = list(range(anio_inicio, anio_actual + 10))

# ==========================================
# 🎨 ESTILOS VISUALES (CSS)
# ==========================================
st.markdown("""
    <style>
    :root { --codesa-black: #121212; --molub-blue: #004a99; --biothan-green: #009640; --gold-bonus: #d4af37; --text-dark: #333333; }
    [data-testid="stSidebar"] { background-color: var(--codesa-black); }
    [data-testid="stSidebar"] * { color: white !important; }
    h1, h2, h3 { color: var(--codesa-black) !important; font-weight: 700 !important; }
    .corporate-subtitle { color: var(--molub-blue); font-weight: 600; margin-top: -10px; margin-bottom: 25px; }
    .user-card { background-color: white; padding: 20px; border-radius: 12px; border-top: 6px solid var(--molub-blue); box-shadow: 0px 4px 12px rgba(0,0,0,0.08); text-align: center; margin-bottom: 20px; height: 100%; display: flex; flex-direction: column; justify-content: space-between; }
    .money-card { background-color: #fffbf0; border-top: 6px solid var(--gold-bonus); padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0px 4px 12px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .kpi-label { font-size: 15px; color: var(--text-dark); font-weight: 700; text-transform: uppercase; margin-bottom: 8px; min-height: 55px; display: flex; align-items: center; justify-content: center;}
    .kpi-value { font-size: 28px; font-weight: 800; color: var(--codesa-black); margin: 5px 0; }
    .kpi-meta { font-size: 12px; color: var(--molub-blue); margin-bottom: 5px; font-weight: bold; background-color: #f0f7ff; padding: 6px; border-radius: 6px; border: 1px solid #dbeafe; min-height: 45px; display: flex; align-items: center; justify-content: center; line-height: 1.2; }
    .kpi-bonus { font-size: 11px; color: #856404; background-color: #fff3cd; border: 1px solid #ffeeba; padding: 4px; border-radius: 4px; margin-bottom: 10px; font-weight: bold; }
    .badge { padding: 8px 10px; border-radius: 8px; font-weight: bold; font-size: 13px; display: block; width: 100%; margin-top: auto;}
    .badge-success { background-color: #e6f4ea; color: var(--biothan-green); border: 2px solid var(--biothan-green); }
    .badge-danger { background-color: #fee2e2; color: #991b1b; border: 2px solid #f87171; }
    @media (max-width: 768px) { .kpi-value { font-size: 24px !important; } .user-card { padding: 15px; margin-bottom: 15px; } }
    </style>
""", unsafe_allow_html=True)

# --- CONSTANTES ---
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
COLUMNAS_BD = ['Año', 'Mes', 'm_ventas', 'm_clientes', 'm_ventas_nuevos', 'm_contenido', 'd_monto_det', 'd_crono_dev', 'd_sat', 'd_seg', 'd_eval', 'd_obra', 'h_ventas', 'h_citas', 'h_mail', 'h_fb', 'h_art']
COLUMNAS_METAS = ['Año', 'meta_mario', 'meta_david', 'meta_hellen', 'premio_mario', 'bono_david', 'bono_hellen']
DEFAULT_DATA = {col: 0.0 if col not in ['Año', 'Mes', 'm_clientes', 'm_contenido', 'd_seg', 'd_obra', 'h_citas', 'h_mail', 'h_fb', 'h_art'] else 0 for col in COLUMNAS_BD if col not in ['Año', 'Mes']}

# ==========================================
# 🔌 SISTEMA ANTICAÍDAS Y CONEXIÓN A BD
# ==========================================
conexion_exitosa = False

if 'df_memoria' not in st.session_state: st.session_state['df_memoria'] = pd.DataFrame(columns=COLUMNAS_BD)
if 'df_metas_memoria' not in st.session_state: st.session_state['df_metas_memoria'] = pd.DataFrame(columns=COLUMNAS_METAS)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_global = conn.read(worksheet="Datos", usecols=list(range(17)), ttl=0).fillna(0)
    cols_numericas = df_global.columns.drop(['Año', 'Mes']) if not df_global.empty else []
    for col in cols_numericas: df_global[col] = pd.to_numeric(df_global[col], errors='coerce').fillna(0)
    
    try:
        # Intentamos leer 7 columnas (incluyendo los premios nuevos)
        df_metas = conn.read(worksheet="Metas", usecols=list(range(7)), ttl=0).fillna(0)
        # Aseguramos que si la hoja era vieja y no tiene las columnas nuevas, se agreguen
        for col in COLUMNAS_METAS:
            if col not in df_metas.columns:
                if col == 'premio_mario': df_metas[col] = 'Viaje Los Cabos'
                elif col == 'bono_david': df_metas[col] = 15000.0
                elif col == 'bono_hellen': df_metas[col] = 25000.0
                else: df_metas[col] = 0.0
                
        for col in ['Año', 'meta_mario', 'meta_david', 'meta_hellen', 'bono_david', 'bono_hellen']: 
            df_metas[col] = pd.to_numeric(df_metas[col], errors='coerce').fillna(0)
        df_metas['premio_mario'] = df_metas['premio_mario'].astype(str)
        
    except Exception: 
        df_metas = pd.DataFrame(columns=COLUMNAS_METAS)

    conexion_exitosa = True
    st.session_state['df_memoria'] = df_global 
    st.session_state['df_metas_memoria'] = df_metas
except Exception:
    df_global = st.session_state['df_memoria']
    df_metas = st.session_state['df_metas_memoria']

# --- LÓGICA DE EXTRACCIÓN DE DATOS ---
def get_month_data(anio, mes):
    global df_global
    filtro = (df_global['Año'] == anio) & (df_global['Mes'] == mes)
    if not df_global[filtro].empty:
        registro = df_global[filtro].iloc[0].to_dict()
        return {**DEFAULT_DATA, **registro} 
    else: return DEFAULT_DATA.copy()

def get_ytd_data(anio):
    global df_global
    filtro_anio = df_global['Año'] == anio
    df_anio = df_global[filtro_anio]
    return {
        'm_ventas': df_anio['m_ventas'].sum() if not df_anio.empty else 0.0,
        'm_clientes': df_anio['m_clientes'].sum() if not df_anio.empty else 0,
        'm_ventas_nuevos': df_anio['m_ventas_nuevos'].sum() if not df_anio.empty else 0.0,
        'd_monto_det': df_anio['d_monto_det'].sum() if not df_anio.empty else 0.0,
        'd_obra': df_anio['d_obra'].sum() if not df_anio.empty else 0,
        'h_ventas': df_anio['h_ventas'].sum() if not df_anio.empty else 0.0
    }

def get_metas_anio(anio):
    global df_metas
    filtro = df_metas['Año'] == anio
    if not df_metas[filtro].empty:
        row = df_metas[filtro].iloc[0]
        return {
            'mario': float(row.get('meta_mario', 10623610.66)), 
            'david': float(row.get('meta_david', 1000000.00)), 
            'hellen': float(row.get('meta_hellen', 1000000.00)),
            'premio_mario': str(row.get('premio_mario', 'Viaje Los Cabos')),
            'bono_david': float(row.get('bono_david', 15000.0)),
            'bono_hellen': float(row.get('bono_hellen', 25000.0))
        }
    else: return {
        'mario': 10623610.66, 'david': 1000000.00, 'hellen': 1000000.00,
        'premio_mario': 'Viaje Los Cabos', 'bono_david': 15000.0, 'bono_hellen': 25000.0
    }

# --- NAVEGACIÓN ---
st.sidebar.title("GRUPO CODESA")
index_anio = ANIOS.index(anio_actual) if anio_actual in ANIOS else 0
anio_seleccionado = st.sidebar.selectbox("📅 AÑO FISCAL:", ANIOS, index=index_anio)
st.sidebar.markdown("---")

OPCIONES_MENU = ["🏠 Vista General (TV)", "👤 Mario Corral", "👷 Arq. David Puga", "👩‍💼 Lic. Hellen García", "🔐 ADMIN (Config & Captura)"]
usuario = st.sidebar.selectbox("Panel de Control:", OPCIONES_MENU)
st.sidebar.markdown("---")

if not conexion_exitosa: st.sidebar.error("⚠️ Sin conexión a Google Sheets. Usando memoria temporal.")

mes_seleccionado = "Vista Anual"
db = {}
if usuario != "🏠 Vista General (TV)" and usuario != "🔐 ADMIN (Config & Captura)":
    mes_seleccionado = st.sidebar.selectbox("🗓️ Mes Operativo:", MESES, index=0)
    db = get_month_data(anio_seleccionado, mes_seleccionado)

ytd = get_ytd_data(anio_seleccionado)
metas_actuales = get_metas_anio(anio_seleccionado)

META_MARIO_ANUAL = metas_actuales['mario']
META_MARIO_MENSUAL = META_MARIO_ANUAL / 12
PREMIO_MARIO = metas_actuales['premio_mario']

META_DAVID_DETECCION_ANUAL = metas_actuales['david']
META_DAVID_MENSUAL = META_DAVID_DETECCION_ANUAL / 12
BONO_DAVID = metas_actuales['bono_david']

META_HELLEN_ANUAL = metas_actuales['hellen']
META_HELLEN_MENSUAL = META_HELLEN_ANUAL / 12
BONO_HELLEN = metas_actuales['bono_hellen']

# --- FUNCIONES VISUALES DE TARJETAS ---
def mostrar_kpi(titulo, actual, meta, descripcion_meta, premio_texto, es_dinero=False, es_inverso=False):
    if es_inverso: cumplio = actual <= meta and actual > 0
    else: cumplio = actual >= meta
    estilo = "badge-success" if cumplio else "badge-danger"
    texto = "LOGRADO" if cumplio else "EN PROCESO"
    icon = "✅" if cumplio else "⚠️"
    val_fmt = f"${actual:,.2f}" if es_dinero else (f"{actual}%" if "Cronograma" in titulo or "Evaluación" in titulo else f"{actual}")
    st.markdown(f"""<div class="user-card"><div class="kpi-label">{titulo}</div><div class="kpi-meta">{descripcion_meta}</div><div class="kpi-value">{val_fmt}</div><div class="kpi-bonus">🎁 {premio_texto}</div><div class="{estilo}">{icon} {texto}</div></div>""", unsafe_allow_html=True)

def mostrar_kpi_digital(h_mail, h_fb, h_art):
    cumplio = (h_mail >= 2) and (h_fb >= 2) and (h_art >= 1)
    estilo = "badge-success" if cumplio else "badge-danger"
    texto = "CUMPLIDO" if cumplio else "PENDIENTE"
    icon = "✅" if cumplio else "⚠️"
    st.markdown(f"""<div class="user-card"><div class="kpi-label">Estrategia Digital Integral</div><div class="kpi-meta">Meta: 2 Mails / 2 FB / 1 Articulo</div><div style="font-size:14px; text-align:left; padding-left:20px;">📧 Mailing: <b>{h_mail}</b>/2<br>📱 Facebook: <b>{h_fb}</b>/2<br>📝 Artículo: <b>{h_art}</b>/1</div><div class="kpi-bonus">🎁 Requisito integral de sueldo</div><div class="{estilo}">{icon} {texto}</div></div>""", unsafe_allow_html=True)

def cartera_mario_acumulada():
    comision_apertura = ytd['m_ventas_nuevos'] * 0.05
    comision_david = ytd['d_monto_det'] * 0.01
    total = comision_apertura + comision_david
    pct_viaje = min(ytd['m_ventas'] / META_MARIO_ANUAL, 1.0) * 100 if META_MARIO_ANUAL > 0 else 0
    st.markdown(f"""<div class="money-card"><h3 style="color:#d4af37 !important;">💰 MI CARTERA {anio_seleccionado} (ACUMULADA)</h3><div style="display:flex; justify-content:space-around;"><div><div style="font-size:12px;">Comisión Nuevos Clientes (5%)</div><div style="font-size:24px; font-weight:bold;">${comision_apertura:,.2f}</div></div><div><div style="font-size:12px;">Comisión Obras Adicionales (1%)</div><div style="font-size:24px; font-weight:bold; color:#004a99;">${comision_david:,.2f}</div></div><div><div style="font-size:12px;">TOTAL ACUMULADO</div><div style="font-size:30px; font-weight:bold; color:#d4af37;">${total:,.2f}</div></div></div><div style="margin-top:10px; background:white; padding:10px; border-radius:8px;"><div style="font-weight:bold;">✈️ Progreso {PREMIO_MARIO} (Meta: ${META_MARIO_ANUAL:,.0f})</div><div style="background:#eee; height:15px; border-radius:10px;"><div style="background:#009640; width:{pct_viaje}%; height:100%; border-radius:10px;"></div></div><div style="font-size:11px; text-align:right;">Monto Alcanzado: ${ytd['m_ventas']:,.0f} ({pct_viaje:.1f}%)</div></div></div>""", unsafe_allow_html=True)

def cartera_david_acumulada():
    comision = ytd['d_monto_det'] * 0.01
    status_bono = f"🔓 ¡GANADO! ${BONO_DAVID:,.0f}" if ytd['d_monto_det'] >= META_DAVID_DETECCION_ANUAL else "🔒 Pendiente de alcanzar"
    st.markdown(f"""<div class="money-card"><h3 style="color:#d4af37 !important;">💰 MI CARTERA {anio_seleccionado} (ACUMULADA)</h3><div style="display:flex; justify-content:space-around;"><div><div style="font-size:12px;">Comisión Obras Adicionales (1%)</div><div style="font-size:28px; font-weight:bold;">${comision:,.2f}</div></div><div><div style="font-size:12px;">Bono Productividad (${BONO_DAVID:,.0f})</div><div style="font-size:20px; font-weight:bold; color:#004a99;">{status_bono}</div></div></div></div>""", unsafe_allow_html=True)

def cartera_hellen_acumulada():
    status_bono = f"🔓 ¡GANADO! ${BONO_HELLEN:,.0f}" if ytd['h_ventas'] >= META_HELLEN_ANUAL else "🔒 Pendiente de alcanzar"
    color_bono = "#009640" if ytd['h_ventas'] >= META_HELLEN_ANUAL else "#888"
    st.markdown(f"""<div class="money-card"><h3 style="color:#d4af37 !important;">💰 MI CARTERA {anio_seleccionado} (ACUMULADA)</h3><div style="display:flex; justify-content:space-around; align-items:center;"><div><div style="font-size:12px;">Ventas de Productos Acumulada</div><div style="font-size:28px; font-weight:bold;">${ytd['h_ventas']:,.2f}</div></div><div><div style="font-size:12px;">Bono por Meta Anual (${BONO_HELLEN:,.0f})</div><div style="font-size:24px; font-weight:bold; color:{color_bono};">{status_bono}</div></div></div></div>""", unsafe_allow_html=True)

# ==========================================
# 📊 PANELES PRINCIPALES (DASHBOARD TV MEJORADO)
# ==========================================

if usuario == "🏠 Vista General (TV)":
    st.markdown(f"<h1 style='text-align:center'>DASHBOARD ESTRATÉGICO {anio_seleccionado}</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    df_chart = df_global[df_global['Año'] == anio_seleccionado].copy()
    if not df_chart.empty:
        df_chart['Mes'] = pd.Categorical(df_chart['Mes'], categories=MESES, ordered=True)
        df_chart = df_chart.sort_values('Mes')

    # --- SECCIÓN MARIO CORRAL ---
    st.markdown("### 👤 MARIO CORRAL | Crecimiento de Ventas de Servicios")
    col_m1, col_m2 = st.columns([1, 3])
    with col_m1:
        st.metric("Ventas de Servicios (YTD)", f"${ytd['m_ventas']:,.0f}")
        pct_mario = min((ytd['m_ventas'] / META_MARIO_ANUAL), 1.0) if META_MARIO_ANUAL > 0 else 0
        st.progress(pct_mario)
        st.caption(f"Meta Anual: ${META_MARIO_ANUAL:,.0f} ({pct_mario*100:.1f}%)")
    with col_m2:
        if not df_chart.empty:
            fig_m = go.Figure()
            fig_m.add_trace(go.Bar(
                x=df_chart['Mes'], y=df_chart['m_ventas'], name='Venta Real', 
                marker=dict(color='rgba(0, 74, 153, 0.8)', line=dict(color='#004a99', width=1.5)),
                text=df_chart['m_ventas'], texttemplate='$%{text:,.2s}', textposition='outside', textfont=dict(size=12, color='#004a99', weight='bold')
            ))
            fig_m.add_trace(go.Scatter(
                x=df_chart['Mes'], y=[META_MARIO_MENSUAL]*len(df_chart), name='Meta Mensual Ideal', 
                mode='lines', line=dict(color='rgba(212, 175, 55, 0.9)', width=2, dash='dash')
            ))
            fig_m.update_layout(
                title=dict(text=f"Evolución Mensual vs Meta (${META_MARIO_MENSUAL:,.0f})", font=dict(size=14, color='#555')),
                height=260, margin=dict(l=10, r=10, t=30, b=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, linecolor='#ddd'), yaxis=dict(showgrid=True, gridcolor='#f4f4f4', showticklabels=False), showlegend=False, hovermode="x unified"
            )
            fig_m.update_traces(cliponaxis=False) 
            st.plotly_chart(fig_m, use_container_width=True)
        else: st.info("Aún no hay datos de ventas registrados para este año.")

    st.markdown("---")

    # --- SECCIÓN DAVID PUGA ---
    st.markdown("### 👷 DAVID PUGA | Oportunidades Generadas en Sitio")
    col_d1, col_d2 = st.columns([1, 3])
    with col_d1:
        st.markdown(f"""<div style="background-color:#e6f4ea; padding:15px; border-radius:10px; text-align:center; border:1px solid #009640;">
            <div style="color:#009640; font-weight:bold; font-size:13px;">OPORTUNIDADES CERRADAS (ACUM)</div>
            <div style="font-size:32px; font-weight:800; color:#121212;">${ytd['d_monto_det']:,.0f}</div></div>""", unsafe_allow_html=True)
        pct_david = min((ytd['d_monto_det'] / META_DAVID_DETECCION_ANUAL), 1.0) if META_DAVID_DETECCION_ANUAL > 0 else 0
        st.markdown("<br>", unsafe_allow_html=True)
        st.progress(pct_david)
        st.caption(f"Meta Anual: ${META_DAVID_DETECCION_ANUAL:,.0f} ({pct_david*100:.1f}%)")
        
    with col_d2:
        if not df_chart.empty:
            fig_d = go.Figure()
            fig_d.add_trace(go.Bar(
                x=df_chart['Mes'], y=df_chart['d_monto_det'], name='Monto Detectado', 
                marker=dict(color='rgba(0, 150, 64, 0.8)', line=dict(color='#009640', width=1.5)),
                text=df_chart['d_monto_det'], texttemplate='$%{text:,.2s}', textposition='outside', textfont=dict(size=12, color='#009640', weight='bold')
            ))
            fig_d.add_trace(go.Scatter(
                x=df_chart['Mes'], y=[META_DAVID_MENSUAL]*len(df_chart), name='Meta Mensual Ideal', 
                mode='lines', line=dict(color='rgba(212, 175, 55, 0.9)', width=2, dash='dash')
            ))
            fig_d.update_layout(
                title=dict(text=f"Monto Detectado por Mes vs Meta (${META_DAVID_MENSUAL:,.0f})", font=dict(size=14, color='#555')),
                height=260, margin=dict(l=10, r=10, t=30, b=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, linecolor='#ddd'), yaxis=dict(showgrid=True, gridcolor='#f4f4f4', showticklabels=False), showlegend=False, hovermode="x unified"
            )
            fig_d.update_traces(cliponaxis=False)
            st.plotly_chart(fig_d, use_container_width=True)

    st.markdown("---")

    # --- SECCIÓN HELLEN GARCÍA ---
    st.markdown("### 👩‍💼 HELLEN GARCÍA | Carrera a la Meta de Productos")
    col_h1, col_h2 = st.columns([1, 3])
    with col_h1:
        st.metric("Ventas de Productos (YTD)", f"${ytd['h_ventas']:,.0f}")
        pct_hellen = min((ytd['h_ventas'] / META_HELLEN_ANUAL), 1.0) if META_HELLEN_ANUAL > 0 else 0
        st.progress(pct_hellen)
        st.caption(f"Meta Anual: ${META_HELLEN_ANUAL:,.0f} ({pct_hellen*100:.1f}%)")
    with col_h2:
        if not df_chart.empty:
            df_chart['Hellen_Acum'] = df_chart['h_ventas'].cumsum()
            df_chart['Meta_Acum'] = [(i+1)*META_HELLEN_MENSUAL for i in range(len(df_chart))]
            
            fig_h = go.Figure()
            fig_h.add_trace(go.Scatter(
                x=df_chart['Mes'], y=df_chart['Hellen_Acum'], mode='lines+markers+text', fill='tozeroy', fillcolor='rgba(0, 150, 64, 0.1)',
                name='Venta Real Acumulada', line=dict(color='#009640', width=3), marker=dict(size=8, color='#009640', line=dict(width=1.5, color='white')),
                text=df_chart['Hellen_Acum'], texttemplate='$%{text:,.2s}', textposition='top left', textfont=dict(size=11, color='#009640', weight='bold')
            ))
            fig_h.add_trace(go.Scatter(
                x=df_chart['Mes'], y=df_chart['Meta_Acum'], name='Trayectoria Ideal', 
                mode='lines', line=dict(color='rgba(212, 175, 55, 0.9)', width=2, dash='dot')
            ))
            fig_h.add_hline(y=META_HELLEN_ANUAL, line_dash="solid", annotation_text=f"🥇 GRAN META ANUAL: ${META_HELLEN_ANUAL:,.0f}", 
                            line_color="rgba(200, 0, 0, 0.3)", line_width=1.5, annotation_position="top left", annotation_font=dict(color="red", size=15, weight="bold"))
            
            fig_h.update_layout(
                title=dict(text="Proyección de Venta Acumulada vs Camino Ideal", font=dict(size=14, color='#555')),
                height=280, margin=dict(l=10, r=10, t=30, b=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, linecolor='#ddd'), yaxis=dict(showgrid=True, gridcolor='#f4f4f4', showticklabels=False), showlegend=False, hovermode="x unified"
            )
            fig_h.update_traces(cliponaxis=False)
            st.plotly_chart(fig_h, use_container_width=True)

# --- PANELES INDIVIDUALES ---
elif usuario == "👤 Mario Corral":
    st.title(f"👤 Mario Corral - {mes_seleccionado} {anio_seleccionado}")
    cartera_mario_acumulada()
    c1, c2, c3 = st.columns(3)
    with c1: mostrar_kpi("Ventas de Servicios", db['m_ventas'], META_MARIO_MENSUAL, f"Meta Mensual: ${META_MARIO_MENSUAL:,.0f}", f"Aporta al {PREMIO_MARIO}", True)
    with c2: mostrar_kpi("Nuevos Clientes Captados", db['m_clientes'], 1, "Meta: Al menos 1 cliente nuevo", "Genera Comisión del 5%")
    with c3: mostrar_kpi("Contenido Técnico Publicado", db['m_contenido'], 2, "Meta: 2 Artículos al mes", "Requisito operativo de liderazgo")

elif usuario == "👷 Arq. David Puga":
    st.title(f"👷 David Puga - {mes_seleccionado} {anio_seleccionado}")
    cartera_david_acumulada()
    c1, c2 = st.columns(2)
    with c1: mostrar_kpi("Oportunidades Detectadas en Obra", db['d_monto_det'], META_DAVID_MENSUAL, f"Meta Mensual: >${META_DAVID_MENSUAL:,.0f} detectados", "Suma para Comisión 1% y Bono extra", True)
    with c2: mostrar_kpi("Desviación de Cronograma y Ppto.", db['d_crono_dev'], 5.0, "Meta: Menor al 5% de desviación", "Requisito para Bono de 1 mes de sueldo", False, True)
    c3, c4 = st.columns(2)
    with c3: mostrar_kpi("Índice de Satisfacción (NPS)", db['d_sat'], 9.0, "Meta: Calificación mínima 9/10", "KPI indispensable de Calidad Post-Venta")
    with c4: mostrar_kpi("Cursos de Seguridad e Higiene", db['d_seg'], 2, "Meta: 2 Cursos impartidos en mes", "KPI indispensable de Seguridad (Bitácora)")

elif usuario == "👩‍💼 Lic. Hellen García":
    st.title(f"👩‍💼 Hellen García - {mes_seleccionado} {anio_seleccionado}")
    cartera_hellen_acumulada()
    c1, c2, c3 = st.columns(3)
    with c1: mostrar_kpi("Ventas de Productos", db['h_ventas'], META_HELLEN_MENSUAL, f"Meta Mensual: ~${META_HELLEN_MENSUAL:,.0f} en facturación", f"Suma acumulado para Bono de ${BONO_HELLEN:,.0f}", True)
    with c2: mostrar_kpi("Citas Generadas (CRM)", db['h_citas'], 4, "Meta: 4 Citas nuevas en el mes", "Motor principal de prospección y ventas")
    with c3: mostrar_kpi_digital(db['h_mail'], db['h_fb'], db['h_art'])

elif usuario == "🔐 ADMIN (Config & Captura)":
    st.title(f"🔐 Panel de Administración: {anio_seleccionado}")
    
    tab_captura, tab_metas = st.tabs(["📝 Captura Mensual", "🎯 Configurar Metas y Premios"])
    
    with tab_captura:
        mes_seleccionado = st.selectbox("Selecciona el mes a capturar:", MESES, index=0)
        st.warning(f"Editando registros de: **{mes_seleccionado} {anio_seleccionado}**")
        db = get_month_data(anio_seleccionado, mes_seleccionado)
        
        with st.form("form_captura"):
            st.markdown("### 1. Indicadores de Mario Corral")
            c1, c2, c3 = st.columns(3)
            v_m = c1.number_input("Facturación Mensual de Servicios ($)", value=float(db['m_ventas']))
            c_m = c2.number_input("Nuevos Clientes Captados (Cantidad)", value=int(db['m_clientes']))
            vn_m = c3.number_input("Monto Facturado a Nuevos Clientes ($)", value=float(db['m_ventas_nuevos']))
            t_m = st.number_input("Artículos de Contenido Técnico Publicados", value=int(db['m_contenido']))
            
            st.markdown("---")
            st.markdown("### 2. Indicadores de David Puga")
            d1, d2 = st.columns(2)
            vm_d = d1.number_input("Monto de Obras Adicionales Detectadas ($)", value=float(db['d_monto_det']))
            vc_d = d1.number_input("Desviación de Cronograma / Presupuesto (%)", value=float(db['d_crono_dev']))
            vo_d = d1.number_input("Cantidad de Cotizaciones Generadas", value=int(db['d_obra']))
            vs_d = d2.number_input("Índice de Satisfacción del Cliente (NPS 0-10)", value=float(db['d_sat']), max_value=10.0)
            vseg_d = d2.number_input("Cursos de Seguridad e Higiene Impartidos", value=int(db['d_seg']))
            ve_d = d2.number_input("Evaluación de Desempeño Personal (%)", value=float(db['d_eval']))
            
            st.markdown("---")
            st.markdown("### 3. Indicadores de Hellen García")
            h1, h2 = st.columns(2)
            v_h = h1.number_input("Facturación Mensual de Productos ($)", value=float(db['h_ventas']))
            vc_h = h2.number_input("Citas Generadas y Registradas (CRM)", value=int(db['h_citas']))
            
            hd1, hd2, hd3 = st.columns(3)
            vm_h = hd1.number_input("Mailings Enviados", value=int(db['h_mail']))
            vf_h = hd2.number_input("Publicaciones en Facebook", value=int(db['h_fb']))
            va_h = hd3.number_input("Artículos de Productos Creados", value=int(db['h_art']))

            if st.form_submit_button("💾 GUARDAR REGISTROS MENSUALES"):
                nuevo_registro = {
                    'Año': anio_seleccionado, 'Mes': mes_seleccionado,
                    'm_ventas': v_m, 'm_clientes': int(c_m), 'm_ventas_nuevos': vn_m, 'm_contenido': int(t_m),
                    'd_monto_det': vm_d, 'd_crono_dev': vc_d, 'd_sat': vs_d, 'd_seg': int(vseg_d), 'd_eval': ve_d, 'd_obra': int(vo_d),
                    'h_ventas': v_h, 'h_citas': int(vc_h), 'h_mail': int(vm_h), 'h_fb': int(vf_h), 'h_art': int(va_h)
                }
                
                filtro = (df_global['Año'] == anio_seleccionado) & (df_global['Mes'] == mes_seleccionado)
                if not df_global[filtro].empty:
                    idx = df_global[filtro].index[0]
                    for key, value in nuevo_registro.items():
                        df_global.at[idx, key] = value
                else:
                    df_global = pd.concat([df_global, pd.DataFrame([nuevo_registro])], ignore_index=True)
                
                if conexion_exitosa:
                    conn.update(worksheet="Datos", data=df_global)
                    st.success("✅ Guardado en Google Sheets correctamente.")
                    st.cache_data.clear() 
                else:
                    st.session_state['df_memoria'] = df_global
                    st.success("✅ Guardado temporalmente (Memoria local).")
                    
    with tab_metas:
        st.info(f"💡 Ajusta las metas y recompensas específicas para el año **{anio_seleccionado}**.")
        
        with st.form("form_metas"):
            
            st.markdown("#### 👤 Mario Corral")
            c_m1, c_m2 = st.columns(2)
            meta_mario = c_m1.number_input("Meta Anual (Servicios $)", value=float(META_MARIO_ANUAL), step=100000.0)
            premio_mario = c_m2.text_input("Premio / Destino del Viaje", value=PREMIO_MARIO)
            
            st.markdown("---")
            st.markdown("#### 👷 David Puga")
            c_d1, c_d2 = st.columns(2)
            meta_david = c_d1.number_input("Meta Anual (Obras Detectadas $)", value=float(META_DAVID_DETECCION_ANUAL), step=50000.0)
            bono_david = c_d2.number_input("Bono por alcanzar la meta ($)", value=float(BONO_DAVID), step=1000.0)
            
            st.markdown("---")
            st.markdown("#### 👩‍💼 Hellen García")
            c_h1, c_h2 = st.columns(2)
            meta_hellen = c_h1.number_input("Meta Anual (Productos $)", value=float(META_HELLEN_ANUAL), step=50000.0)
            bono_hellen = c_h2.number_input("Bono por alcanzar la meta ($)", value=float(BONO_HELLEN), step=1000.0)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("🎯 GUARDAR METAS Y PREMIOS"):
                nuevo_registro_meta = {
                    'Año': anio_seleccionado, 
                    'meta_mario': meta_mario, 
                    'meta_david': meta_david, 
                    'meta_hellen': meta_hellen,
                    'premio_mario': premio_mario,
                    'bono_david': bono_david,
                    'bono_hellen': bono_hellen
                }
                
                filtro_metas = df_metas['Año'] == anio_seleccionado
                if not df_metas[filtro_metas].empty:
                    idx_meta = df_metas[filtro_metas].index[0]
                    for key, value in nuevo_registro_meta.items():
                        df_metas.at[idx_meta, key] = value
                else:
                    df_metas = pd.concat([df_metas, pd.DataFrame([nuevo_registro_meta])], ignore_index=True)
                
                if conexion_exitosa:
                    conn.update(worksheet="Metas", data=df_metas)
                    st.success(f"✅ Nuevas metas y premios para {anio_seleccionado} actualizadas en la nube.")
                    st.cache_data.clear()
                    st.rerun() 
                else:
                    st.session_state['df_metas_memoria'] = df_metas
                    st.success("✅ Metas actualizadas temporalmente.")
                    st.rerun()