# -*- coding: utf-8 -*-
"""
1_Dashboard.py — Tablero de indicadores (estilo Power BI)
=========================================================
Muestra KPIs y graficos interactivos (Plotly) sobre el consumo de cuero
y el estado del inventario. Todos los datos provienen del Excel.
"""

import os
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import loader as L
from utils import ui

st.set_page_config(page_title="Dashboard · Piolito", page_icon="📊", layout="wide")
ui.aplicar_estilos()
ui.marca_sidebar()

# ---------------------------------------------------------------------------
# Carga de datos
# ---------------------------------------------------------------------------
modelos = L.cargar_modelos()
inventario = L.cargar_inventario()
pedidos = L.cargar_pedidos()
historial = L.cargar_historial()

ui.encabezado("Dashboard", "Visión general del consumo de cuero y del estado del inventario.")

# ---------------------------------------------------------------------------
# Filtros (barra lateral)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔎 Filtros")
    temporadas = sorted(modelos[L.COL_M_TEMPORADA].dropna().unique().tolist())
    categorias = sorted(modelos[L.COL_M_CATEGORIA].dropna().unique().tolist())

    f_temporada = st.multiselect("Temporada", temporadas, default=temporadas)
    f_categoria = st.multiselect("Categoría", categorias, default=categorias)

# Aplicar filtros a modelos
modelos_f = modelos[
    modelos[L.COL_M_TEMPORADA].isin(f_temporada)
    & modelos[L.COL_M_CATEGORIA].isin(f_categoria)
].copy()

codigos_filtrados = set(modelos_f[L.COL_M_CODIGO].tolist())

# Pedidos enriquecidos con temporada/categoria del modelo
ped = pedidos.merge(
    modelos[[L.COL_M_CODIGO, L.COL_M_TEMPORADA, L.COL_M_CATEGORIA]],
    left_on=L.COL_P_COD_MODELO,
    right_on=L.COL_M_CODIGO,
    how="left",
    suffixes=("", "_m"),
)
ped_f = ped[ped[L.COL_P_COD_MODELO].isin(codigos_filtrados)].copy()

# Historial filtrado por los modelos seleccionados
hist_f = historial[historial[L.COL_H_COD_MODELO].isin(codigos_filtrados)].copy()

# ---------------------------------------------------------------------------
# Fila de KPIs
# ---------------------------------------------------------------------------
total_modelos = len(modelos_f)
stock_total = float(inventario[L.COL_I_STOCK].sum())
mask_critico = inventario[L.COL_I_STOCK] < inventario[L.COL_I_STOCK_MIN]
stock_disponible = float(inventario.loc[~mask_critico, L.COL_I_STOCK].sum())
n_criticos = int(mask_critico.sum())

# Consumo total proyectado = consumo requerido de pedidos aun no terminados
activos = ped_f[ped_f[L.COL_P_ESTADO].isin(["Pendiente", "En producción"])]
consumo_proyectado = float(activos[L.COL_P_CONSUMO].sum())

# Consumo promedio por modelo (m² por par)
consumo_prom = float(modelos_f[L.COL_M_CONSUMO].mean()) if total_modelos else 0.0

k1, k2, k3 = st.columns(3)
with k1:
    ui.kpi_card("Total de modelos", f"{total_modelos}", "👟", ui.COLORES["violeta"],
                "modelos registrados")
with k2:
    ui.kpi_card("Stock total de cuero", f"{stock_total:,.0f} m²", "🧵", ui.COLORES["azul"],
                "suma de todo el inventario")
with k3:
    ui.kpi_card("Stock disponible", f"{stock_disponible:,.0f} m²", "✅", ui.COLORES["verde"],
                "materiales sin alerta")

st.write("")
k4, k5, k6 = st.columns(3)
with k4:
    ui.kpi_card("Materiales en stock crítico", f"{n_criticos}", "⚠️", ui.COLORES["rojo"],
                "por debajo del mínimo")
with k5:
    ui.kpi_card("Consumo total proyectado", f"{consumo_proyectado:,.0f} m²", "📈",
                ui.COLORES["ambar"], "pedidos pendientes / en producción")
with k6:
    ui.kpi_card("Consumo promedio por modelo", f"{consumo_prom:.2f} m²", "🎯",
                ui.COLORES["coral"], "cuero por par")

st.write("")
st.divider()

# ---------------------------------------------------------------------------
# Plantilla visual común para los graficos
# ---------------------------------------------------------------------------
# IMPORTANTE: la leyenda NO se define aqui. Cada grafico decide donde poner su
# leyenda para que NUNCA quede encima del area de datos ni sobre las etiquetas
# rotadas del eje X. Los graficos de barras con etiquetas inclinadas reciben
# margen inferior amplio; los que tienen leyenda la colocan ARRIBA del grafico.
ALTURA = 360  # alto fijo de cada grafico (px) para que la maquetacion no "baile"

LAYOUT = dict(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(family="Nunito, Segoe UI, sans-serif", color="#241B4B", size=13),
    margin=dict(l=12, r=12, t=24, b=12),
    height=ALTURA,
    showlegend=False,
)

# Leyenda horizontal colocada ARRIBA del area de trazado (no la tapa)
LEYENDA_ARRIBA = dict(
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                bgcolor="rgba(0,0,0,0)"),
)


def card_open(titulo):
    st.markdown(
        f'<div style="background:#fff;border:1px solid #ECE7F6;border-radius:18px;'
        f'padding:8px 16px 14px 16px;box-shadow:0 6px 20px rgba(54,38,110,0.05);'
        f'margin-bottom:18px;">'
        f'<div style="font-weight:800;color:#241B4B;font-size:15px;'
        f"font-family:'Baloo 2',sans-serif;padding:8px 4px 4px 4px;\">"
        f'{titulo}</div>',
        unsafe_allow_html=True,
    )


def card_close():
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Fila 1 de graficos: consumo por modelo  +  consumo por temporada
# ---------------------------------------------------------------------------
g1, g2 = st.columns([1.4, 1])

with g1:
    card_open("Consumo de cuero por modelo (m²)")
    consumo_modelo = (
        ped_f.groupby(L.COL_P_COD_MODELO)[L.COL_P_CONSUMO]
        .sum()
        .reset_index()
        .sort_values(L.COL_P_CONSUMO, ascending=False)
    )
    if consumo_modelo.empty:
        st.info("No hay pedidos para los filtros seleccionados.")
    else:
        fig = px.bar(
            consumo_modelo,
            x=L.COL_P_COD_MODELO,
            y=L.COL_P_CONSUMO,
            color_discrete_sequence=[ui.COLORES["violeta"]],
        )
        fig.update_layout(**LAYOUT)
        fig.update_layout(margin=dict(l=12, r=12, t=24, b=110))
        fig.update_xaxes(title="", tickangle=-45, showgrid=False)
        fig.update_yaxes(title="m²", gridcolor="#EEF0F6")
        st.plotly_chart(fig, use_container_width=True)
    card_close()

with g2:
    card_open("Consumo por temporada (m²)")
    consumo_temp = (
        ped_f.groupby(L.COL_M_TEMPORADA)[L.COL_P_CONSUMO].sum().reset_index()
    )
    consumo_temp = consumo_temp[consumo_temp[L.COL_P_CONSUMO] > 0]
    if consumo_temp.empty:
        st.info("Sin datos para los filtros seleccionados.")
    else:
        fig = px.pie(
            consumo_temp,
            names=L.COL_M_TEMPORADA,
            values=L.COL_P_CONSUMO,
            hole=0.55,
            color_discrete_sequence=ui.PALETA_PLOTLY,
        )
        fig.update_traces(textposition="inside", textinfo="percent")
        fig.update_layout(**LAYOUT)
        fig.update_layout(showlegend=True, margin=dict(l=12, r=12, t=24, b=60),
                          legend=dict(orientation="h", yanchor="top", y=-0.02,
                                      xanchor="center", x=0.5))
        st.plotly_chart(fig, use_container_width=True)
    card_close()

# ---------------------------------------------------------------------------
# Fila 2: top modelos  +  stock por material
# ---------------------------------------------------------------------------
g3, g4 = st.columns(2)

with g3:
    card_open("Top 10 modelos con mayor consumo (m²)")
    top = (
        ped_f.groupby(L.COL_P_COD_MODELO)[L.COL_P_CONSUMO]
        .sum()
        .reset_index()
        .sort_values(L.COL_P_CONSUMO, ascending=True)
        .tail(10)
    )
    if top.empty:
        st.info("Sin datos para los filtros seleccionados.")
    else:
        fig = px.bar(
            top,
            x=L.COL_P_CONSUMO,
            y=L.COL_P_COD_MODELO,
            orientation="h",
            color=L.COL_P_CONSUMO,
            color_continuous_scale=["#D9CCF7", "#6C4BD8"],
        )
        fig.update_layout(**LAYOUT, coloraxis_showscale=False)
        fig.update_xaxes(title="m²", gridcolor="#EEF0F6")
        fig.update_yaxes(title="", showgrid=False)
        st.plotly_chart(fig, use_container_width=True)
    card_close()

with g4:
    card_open("Stock disponible por material (m²)")
    inv = inventario.copy()
    inv["material"] = inv[L.COL_I_TIPO_CUERO] + " · " + inv[L.COL_I_COLOR]
    inv = inv.sort_values(L.COL_I_STOCK, ascending=False)
    fig = px.bar(
        inv,
        x="material",
        y=L.COL_I_STOCK,
        color_discrete_sequence=[ui.COLORES["azul"]],
    )
    fig.update_layout(**LAYOUT)
    fig.update_layout(margin=dict(l=12, r=12, t=24, b=130))
    fig.update_xaxes(title="", tickangle=-30, showgrid=False)
    fig.update_yaxes(title="m²", gridcolor="#EEF0F6")
    st.plotly_chart(fig, use_container_width=True)
    card_close()

# ---------------------------------------------------------------------------
# Fila 3: estado del inventario  +  comparacion stock vs minimo
# ---------------------------------------------------------------------------
g5, g6 = st.columns([1, 1.4])

with g5:
    card_open("Estado del inventario")
    estado_counts = inventario[L.COL_I_ESTADO].value_counts().reset_index()
    estado_counts.columns = ["estado", "cantidad"]
    mapa_color = {"OK": ui.COLORES["verde"], "Crítico": ui.COLORES["coral"]}
    fig = px.pie(
        estado_counts,
        names="estado",
        values="cantidad",
        hole=0.55,
        color="estado",
        color_discrete_map=mapa_color,
    )
    fig.update_traces(textposition="inside", textinfo="value+label")
    fig.update_layout(**LAYOUT)
    fig.update_layout(showlegend=True, margin=dict(l=12, r=12, t=24, b=60),
                      legend=dict(orientation="h", yanchor="top", y=-0.02,
                                  xanchor="center", x=0.5))
    st.plotly_chart(fig, use_container_width=True)
    card_close()

with g6:
    card_open("Comparación: stock disponible vs stock mínimo")
    inv = inventario.copy()
    inv["material"] = inv[L.COL_I_TIPO_CUERO] + " · " + inv[L.COL_I_COLOR]
    fig = go.Figure()
    fig.add_bar(
        x=inv["material"], y=inv[L.COL_I_STOCK],
        name="Stock disponible", marker_color=ui.COLORES["violeta"],
    )
    fig.add_bar(
        x=inv["material"], y=inv[L.COL_I_STOCK_MIN],
        name="Stock mínimo", marker_color=ui.COLORES["ambar"],
    )
    fig.update_layout(**LAYOUT, barmode="group")
    # Leyenda ARRIBA + margen inferior amplio para las etiquetas inclinadas
    fig.update_layout(**LEYENDA_ARRIBA, margin=dict(l=12, r=12, t=40, b=130))
    fig.update_xaxes(title="", tickangle=-30, showgrid=False)
    fig.update_yaxes(title="m²", gridcolor="#EEF0F6")
    st.plotly_chart(fig, use_container_width=True)
    card_close()

st.caption("Los filtros de la barra lateral afectan a los indicadores y graficos basados en modelos y pedidos.")
