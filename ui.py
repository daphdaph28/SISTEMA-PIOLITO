# -*- coding: utf-8 -*-
"""
ui.py
-----
Funciones de presentacion compartidas por todas las paginas.

Identidad visual basada en el logo de Piolito (calzado infantil):
  Violeta   #6C4BD8   (color primario / fondo del logo)
  Amarillo  #F6C544   (pollitos)
  Coral     #F2603C   (texto "Piolito")
  Verde     #2FB463   (estados OK / positivos)
  Ambar     #F5A524   (advertencias)
  Rojo      #E5484D   (alertas / stock critico)

Look general: cálido, redondeado y amigable para los trabajadores, pero
ordenado y profesional (tipo panel BI).

Funciones:
  * aplicar_estilos()  -> inyecta el CSS global + fuentes.
  * marca_sidebar()    -> logo de Piolito + nombre en la barra lateral.
  * encabezado()       -> eyebrow + titulo + subtitulo de cada pagina.
  * kpi_card()         -> tarjeta KPI con valor, etiqueta e icono.
  * hero()             -> banner de bienvenida (portada).
"""

import os
import base64

import streamlit as st

# --- Rutas ---
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo_piolito.png")

# Paleta de colores reutilizable en los graficos Plotly
COLORES = {
    "violeta": "#6C4BD8",
    "violeta_claro": "#A78BFA",
    "navy": "#241B4B",
    "amarillo": "#F6C544",
    "coral": "#F2603C",
    "verde": "#2FB463",
    "ambar": "#F5A524",
    "rojo": "#E5484D",
    "azul": "#4A8DF0",
    "rosa": "#EC4899",
    "teal": "#14B8A6",
    "gris": "#94A3B8",
}

# Secuencia de colores para series categoricas en Plotly (alegre pero ordenada)
PALETA_PLOTLY = [
    "#6C4BD8", "#F6C544", "#2FB463", "#4A8DF0",
    "#F2603C", "#A78BFA", "#14B8A6", "#EC4899",
    "#F5A524", "#6366F1",
]


def _logo_base64():
    """Devuelve el logo como cadena base64 para incrustarlo en HTML."""
    try:
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except OSError:
        return ""


def aplicar_estilos():
    """Inyecta el CSS global + fuentes. Llamar al inicio de cada pagina."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Nunito:wght@400;500;600;700;800&display=swap');

        /* ---- Tipografia y fondo general ---- */
        html, body, [class*="css"], .stApp, p, span, div, label {
            font-family: 'Nunito', system-ui, sans-serif;
        }
        .stApp {
            background:
                radial-gradient(900px 500px at 100% -10%, #EFE9FF 0%, rgba(239,233,255,0) 55%),
                radial-gradient(700px 400px at -5% 0%, #FFF6E6 0%, rgba(255,246,230,0) 50%),
                #F7F5FB;
        }
        .block-container { padding-top: 2.2rem; }

        /* ---- Barra lateral ---- */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #2A1F57 0%, #3A2A78 100%);
            border-right: none;
        }
        section[data-testid="stSidebar"] * { color: #ECE8FA !important; }
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stMultiSelect label,
        section[data-testid="stSidebar"] .stRadio label {
            color: #CFC6F2 !important; font-weight: 700;
        }
        /* Items del menu de paginas */
        section[data-testid="stSidebarNav"] a {
            border-radius: 12px; margin: 2px 8px; padding: 6px 10px;
            transition: background .15s ease;
        }
        section[data-testid="stSidebarNav"] a:hover {
            background: rgba(255,255,255,0.10);
        }
        section[data-testid="stSidebarNav"] a[aria-current="page"] {
            background: rgba(246,197,68,0.18);
        }

        /* ---- Tarjetas KPI ---- */
        .kpi-card {
            position: relative; overflow: hidden;
            background: #FFFFFF;
            border: 1px solid #ECE7F6;
            border-radius: 20px;
            padding: 18px 20px 16px 20px;
            box-shadow: 0 6px 20px rgba(54, 38, 110, 0.07);
            height: 100%;
            transition: transform .16s ease, box-shadow .16s ease;
        }
        .kpi-card::before {
            content:""; position:absolute; top:0; left:0; right:0; height:5px;
            background: var(--accent, #6C4BD8);
        }
        .kpi-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 28px rgba(54, 38, 110, 0.13);
        }
        .kpi-icon {
            width: 46px; height: 46px; border-radius: 14px;
            display: flex; align-items: center; justify-content: center;
            font-size: 23px;
        }
        .kpi-label {
            color: #6B7280; font-size: 13.5px; font-weight: 700;
            margin-top: 14px; letter-spacing: .1px;
        }
        .kpi-value {
            color: #241B4B; font-size: 32px; font-weight: 800;
            font-family: 'Baloo 2', 'Nunito', sans-serif;
            line-height: 1.05; margin-top: 2px;
        }
        .kpi-sub { color: #9AA0AE; font-size: 12px; margin-top: 4px; font-weight: 600; }

        /* ---- Encabezado de pagina ---- */
        .eyebrow {
            display:inline-block; font-size:12px; font-weight:800; letter-spacing:1.2px;
            text-transform:uppercase; color:#6C4BD8; background:#EFE9FF;
            padding:4px 12px; border-radius:999px;
        }
        .page-title {
            color: #241B4B; font-size: 33px; font-weight: 800;
            font-family: 'Baloo 2', 'Nunito', sans-serif;
            margin: 8px 0 0 0; line-height:1.1;
        }
        .page-sub { color: #6B7280; font-size: 15px; margin: 3px 0 6px 0; font-weight:600; }
        .pill {
            display:inline-block; padding:5px 13px; border-radius:999px;
            font-size:12.5px; font-weight:800;
        }

        /* ---- Botones ---- */
        .stButton > button, .stDownloadButton > button, div[data-testid="stFormSubmitButton"] > button {
            border-radius: 13px; font-weight: 800; font-family:'Nunito',sans-serif;
            border: 1.5px solid #E3DCF4;
        }
        .stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"],
        div[data-testid="stFormSubmitButton"] > button[kind="primary"] {
            background: #6C4BD8; border-color:#6C4BD8;
        }
        div[data-testid="stForm"] {
            border: 1px solid #ECE7F6; border-radius: 20px;
            padding: 10px 20px 6px 20px; background: #FFFFFF;
            box-shadow: 0 6px 20px rgba(54,38,110,0.05);
        }
        h4, h5, h3 { color:#241B4B; font-family:'Baloo 2','Nunito',sans-serif; }
        .stDataFrame { border-radius: 14px; overflow:hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def marca_sidebar():
    """Muestra el logo de Piolito y el nombre del sistema en la barra lateral."""
    logo = _logo_base64()
    logo_html = (
        f'<img src="data:image/png;base64,{logo}" '
        f'style="width:100%;border-radius:14px;display:block;" alt="Piolito"/>'
        if logo else '<div style="font-size:30px;">👟</div>'
    )
    with st.sidebar:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border-radius:18px; padding:12px;
                        margin:2px 2px 10px 2px; box-shadow:0 6px 16px rgba(0,0,0,0.18);">
                {logo_html}
            </div>
            <div style="text-align:center; margin-bottom:6px;">
                <div style="font-family:'Baloo 2',sans-serif; font-weight:800; font-size:17px;
                            color:#FFFFFF !important;">Sistema Piolito</div>
                <div style="font-size:12px; color:#CFC6F2 !important;">
                    Planificación de cuero</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def encabezado(titulo, subtitulo="", eyebrow="PIOLITO · CALZADO INFANTIL"):
    """Eyebrow + titulo grande + subtitulo para la parte superior de cada pagina."""
    eb = f'<span class="eyebrow">{eyebrow}</span>' if eyebrow else ""
    st.markdown(
        f"""
        <div style="margin-bottom:16px;">
            {eb}
            <p class="page-title">{titulo}</p>
            <p class="page-sub">{subtitulo}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label, value, icon="📊", color="#6C4BD8", sub=""):
    """Renderiza una tarjeta KPI. Usar dentro de una columna st.columns()."""
    bg = _tint(color)
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    st.markdown(
        f"""
        <div class="kpi-card" style="--accent:{color};">
            <div class="kpi-icon" style="background:{bg}; color:{color};">{icon}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero(logo=True):
    """Banner de bienvenida para la portada (app.py)."""
    logo_b64 = _logo_base64() if logo else ""
    logo_img = (
        f'<img src="data:image/png;base64,{logo_b64}" '
        f'style="height:74px;border-radius:14px;box-shadow:0 6px 16px rgba(0,0,0,0.18);"/>'
        if logo_b64 else ""
    )
    st.markdown(
        f"""
        <div style="background:linear-gradient(120deg,#6C4BD8 0%,#8B5BE0 55%,#A24BD8 100%);
                    border-radius:24px; padding:30px 34px; color:#fff;
                    box-shadow:0 14px 34px rgba(108,75,216,0.30);
                    display:flex; align-items:center; gap:24px; flex-wrap:wrap;">
            <div style="flex:1; min-width:260px;">
                <div style="font-size:13px;font-weight:800;letter-spacing:1.5px;opacity:.85;">
                    CALZADO INFANTIL PIOLITO</div>
                <div style="font-family:'Baloo 2',sans-serif;font-weight:800;font-size:34px;
                            line-height:1.1;margin-top:6px;">
                    Planificación de consumo de cuero 👟</div>
                <div style="font-size:15.5px;opacity:.92;margin-top:10px;max-width:620px;line-height:1.55;">
                    Calcula cuánto cuero necesitas, controla tu inventario y toma decisiones
                    de compra. Toda la información sale directo de tu archivo Excel.</div>
            </div>
            <div>{logo_img}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _tint(hex_color):
    """Devuelve una version muy clara del color para el fondo del icono."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, 0.14)"
