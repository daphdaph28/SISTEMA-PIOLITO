# -*- coding: utf-8 -*-
"""
app.py — Pagina principal del Sistema de Planificacion de Cuero · Piolito
=========================================================================

Calzado infantil Piolito — herramienta universitaria para:
  * Planificar el consumo de cuero por modelo y cantidad de pares.
  * Controlar el inventario de cuero.
  * Apoyar la toma de decisiones (dashboard, chatbot, reportes).

Ejecutar con:
    streamlit run app.py

Toda la informacion proviene de un unico archivo Excel:
    data/Base_Piolito.xlsx
"""

import os
import sys

import streamlit as st

# Asegura que la raiz del proyecto este en el path para importar 'utils'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import loader as L
from utils import ui

# ---------------------------------------------------------------------------
# Configuracion general de la pagina
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Piolito · Planificacion de Cuero",
    page_icon="👟",
    layout="wide",
    initial_sidebar_state="expanded",
)

ui.aplicar_estilos()

# ---------------------------------------------------------------------------
# Barra lateral (marca + navegacion + info)
# ---------------------------------------------------------------------------
ui.marca_sidebar()
with st.sidebar:
    st.caption("Navega entre los módulos usando el menú de páginas de arriba ⬆️")
    st.divider()
    if L.excel_existe():
        st.success("Base de datos Excel conectada", icon="✅")
    else:
        st.error("No se encontro data/Base_Piolito.xlsx", icon="⚠️")

# ---------------------------------------------------------------------------
# Verificacion del archivo de datos
# ---------------------------------------------------------------------------
if not L.excel_existe():
    st.error(
        "No se encontro el archivo **data/Base_Piolito.xlsx**. "
        "Coloca el Excel en la carpeta `data/` y recarga la pagina."
    )
    st.stop()

# Cargar datos para mostrar un resumen rapido
modelos = L.cargar_modelos()
inventario = L.cargar_inventario()
pedidos = L.cargar_pedidos()

# ---------------------------------------------------------------------------
# Portada
# ---------------------------------------------------------------------------
ui.hero()

st.write("")

# Resumen rapido en tarjetas
c1, c2, c3, c4 = st.columns(4)
with c1:
    ui.kpi_card("Modelos registrados", f"{len(modelos)}", "👟", ui.COLORES["violeta"])
with c2:
    stock_total = float(inventario[L.COL_I_STOCK].sum())
    ui.kpi_card("Stock total de cuero", f"{stock_total:,.0f} m²", "🧵", ui.COLORES["azul"])
with c3:
    criticos = int((inventario[L.COL_I_ESTADO] == "Crítico").sum())
    ui.kpi_card("Materiales en stock crítico", f"{criticos}", "⚠️", ui.COLORES["coral"])
with c4:
    ui.kpi_card("Pedidos registrados", f"{len(pedidos)}", "📦", ui.COLORES["verde"])

st.write("")

# Guia de modulos
st.markdown("#### ¿Que puedes hacer aqui?")
g1, g2, g3 = st.columns(3)
modulos = [
    ("📊 Dashboard", "KPIs y graficos interactivos del consumo y el inventario."),
    ("💬 Chatbot", "Pregunta en lenguaje natural cuanto cuero necesitas."),
    ("👟 Modelos", "Consulta y registra nuevos modelos de calzado."),
    ("📦 Inventario", "Controla entradas, salidas, stock y alertas."),
    ("📑 Reportes", "Exporta inventario, consumo y modelos a Excel."),
]
cols = [g1, g2, g3, g1, g2]
for (titulo, desc), col in zip(modulos, cols):
    with col:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1.5px solid #E8EAF0; border-radius:14px;
                        padding:16px 18px; margin-bottom:14px;">
                <div style="font-weight:700; color:#1A2844; font-size:15px;">{titulo}</div>
                <div style="color:#64748B; font-size:13px; margin-top:4px;">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.caption(
    "Proyecto universitario · Python + Streamlit + Pandas + Plotly + OpenPyXL · "
    "Sin bases de datos SQL ni IA externa."
)
