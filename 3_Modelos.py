# -*- coding: utf-8 -*-
"""
3_Modelos.py — Catálogo de modelos
==================================
Tabla interactiva con todos los modelos de calzado y formulario para
registrar nuevos modelos. Al guardar, el nuevo modelo se escribe
automáticamente en la hoja MODELOS del Excel.
"""

import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import loader as L
from utils import ui

st.set_page_config(page_title="Modelos · Piolito", page_icon="👟", layout="wide")
ui.aplicar_estilos()
ui.marca_sidebar()

modelos = L.cargar_modelos()
inventario = L.cargar_inventario()

ui.encabezado("Modelos", "Consulta el catálogo y registra nuevos modelos de calzado.")

# ---------------------------------------------------------------------------
# Resumen
# ---------------------------------------------------------------------------
c1, c2, c3 = st.columns(3)
with c1:
    ui.kpi_card("Modelos registrados", f"{len(modelos)}", "👟", ui.COLORES["violeta"])
with c2:
    activos = int((modelos[L.COL_M_ESTADO] == "Activo").sum())
    ui.kpi_card("Modelos activos", f"{activos}", "✅", ui.COLORES["verde"])
with c3:
    prom = float(modelos[L.COL_M_CONSUMO].mean())
    ui.kpi_card("Consumo promedio por par", f"{prom:.2f} m²", "📏", ui.COLORES["azul"])

st.write("")

# ---------------------------------------------------------------------------
# Tabla interactiva con filtros
# ---------------------------------------------------------------------------
st.markdown("#### Catálogo de modelos")

fc1, fc2, fc3 = st.columns([2, 1, 1])
with fc1:
    busqueda = st.text_input("Buscar (código, modelo, color…)", "")
with fc2:
    cat_opts = ["Todas"] + sorted(modelos[L.COL_M_CATEGORIA].dropna().unique().tolist())
    f_cat = st.selectbox("Categoría", cat_opts)
with fc3:
    est_opts = ["Todos"] + sorted(modelos[L.COL_M_ESTADO].dropna().unique().tolist())
    f_est = st.selectbox("Estado", est_opts)

vista = modelos.copy()
if busqueda.strip():
    q = busqueda.strip().lower()
    mask = vista.apply(lambda r: q in " ".join(map(str, r.values)).lower(), axis=1)
    vista = vista[mask]
if f_cat != "Todas":
    vista = vista[vista[L.COL_M_CATEGORIA] == f_cat]
if f_est != "Todos":
    vista = vista[vista[L.COL_M_ESTADO] == f_est]

st.dataframe(
    vista,
    use_container_width=True,
    hide_index=True,
    column_config={
        L.COL_M_CONSUMO: st.column_config.NumberColumn(format="%.2f m²"),
        L.COL_M_PRECIO: st.column_config.NumberColumn(format="S/ %.2f"),
    },
)
st.caption(f"Mostrando {len(vista)} de {len(modelos)} modelos.")

st.divider()

# ---------------------------------------------------------------------------
# Formulario: registrar nuevo modelo
# ---------------------------------------------------------------------------
st.markdown("#### ➕ Registrar nuevo modelo")
st.caption("El nuevo modelo se guardará automáticamente en el archivo Excel (hoja MODELOS).")

# Opciones derivadas de los datos existentes
cats = sorted(modelos[L.COL_M_CATEGORIA].dropna().unique().tolist())
subcats = sorted(modelos[L.COL_M_SUBCATEGORIA].dropna().unique().tolist())
generos = sorted(modelos[L.COL_M_GENERO].dropna().unique().tolist())
temporadas = sorted(modelos[L.COL_M_TEMPORADA].dropna().unique().tolist())
tipos_cuero = sorted(inventario[L.COL_I_TIPO_CUERO].dropna().unique().tolist())
colores = sorted(inventario[L.COL_I_COLOR].dropna().unique().tolist())

with st.form("nuevo_modelo", clear_on_submit=True):
    f1, f2, f3 = st.columns(3)
    with f1:
        codigo = st.text_input("Código *", placeholder="Ej. BP-011")
        categoria = st.selectbox("Categoría *", cats)
        genero = st.selectbox("Género *", generos)
        tipo_cuero = st.selectbox("Tipo de cuero *", tipos_cuero)
    with f2:
        nombre = st.text_input("Nombre del modelo", placeholder="Ej. BP-011")
        subcategoria = st.selectbox("Subcategoría", subcats)
        temporada = st.selectbox("Temporada *", temporadas)
        color = st.selectbox("Color *", colores)
    with f3:
        talla_ini = st.number_input("Talla inicial", min_value=10, max_value=40, value=15)
        talla_fin = st.number_input("Talla final", min_value=10, max_value=45, value=19)
        consumo = st.number_input("Consumo por par (m²) *", min_value=0.01,
                                  max_value=5.0, value=0.22, step=0.01, format="%.2f")
        precio = st.number_input("Precio venta S/", min_value=0.0, value=170.0, step=5.0)

    estado = st.selectbox("Estado", ["Activo", "Inactivo"])
    observaciones = st.text_area("Observaciones", placeholder="Notas internas (opcional)")

    enviado = st.form_submit_button("💾 Guardar modelo", type="primary",
                                    use_container_width=True)

if enviado:
    # Validaciones
    if not codigo.strip():
        st.error("El **código** es obligatorio.")
    elif codigo.strip().upper() in modelos[L.COL_M_CODIGO].astype(str).str.upper().tolist():
        st.error(f"Ya existe un modelo con el código **{codigo.strip().upper()}**.")
    else:
        # Construir la nueva fila respetando las columnas reales de la hoja
        nueva = {col: "" for col in modelos.columns}
        nueva[L.COL_M_CODIGO] = codigo.strip().upper()
        nueva[L.COL_M_MODELO] = nombre.strip() or codigo.strip().upper()
        nueva[L.COL_M_CATEGORIA] = categoria
        nueva[L.COL_M_SUBCATEGORIA] = subcategoria
        nueva[L.COL_M_GENERO] = genero
        nueva[L.COL_M_TEMPORADA] = temporada
        nueva[L.COL_M_TIPO_CUERO] = tipo_cuero
        nueva[L.COL_M_COLOR] = color
        nueva[L.COL_M_TALLA_INI] = int(talla_ini)
        nueva[L.COL_M_TALLA_FIN] = int(talla_fin)
        nueva[L.COL_M_CONSUMO] = round(float(consumo), 2)
        nueva[L.COL_M_PRECIO] = round(float(precio), 2)
        nueva[L.COL_M_ESTADO] = estado
        # Si la hoja tuviera una columna de observaciones, se completaria;
        # si no existe, la nota no rompe el esquema.
        if "Observaciones" in modelos.columns:
            nueva["Observaciones"] = observaciones.strip()

        actualizado = pd.concat([modelos, pd.DataFrame([nueva])], ignore_index=True)
        L.guardar_hoja(L.HOJA_MODELOS, actualizado)
        st.success(f"Modelo **{nueva[L.COL_M_CODIGO]}** registrado y guardado en el Excel.",
                   icon="✅")
        st.rerun()
