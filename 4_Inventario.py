# -*- coding: utf-8 -*-
"""
4_Inventario.py — Control de inventario de cuero
================================================
Muestra el inventario de cuero, permite registrar entradas y salidas, ver el
stock disponible y el stock mínimo, y genera una alerta visual automática
cuando algún material cae por debajo de su mínimo. Los cambios se guardan
directamente en el Excel (hoja INVENTARIO_CUERO).
"""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import loader as L
from utils import ui

st.set_page_config(page_title="Inventario · Piolito", page_icon="📦", layout="wide")
ui.aplicar_estilos()
ui.marca_sidebar()

inventario = L.cargar_inventario()

ui.encabezado("Inventario de cuero", "Controla el stock, registra movimientos y revisa las alertas.")

# ---------------------------------------------------------------------------
# Indicadores
# ---------------------------------------------------------------------------
stock_total = float(inventario[L.COL_I_STOCK].sum())
mask_critico = inventario[L.COL_I_STOCK] < inventario[L.COL_I_STOCK_MIN]
criticos = inventario[mask_critico]
valor_inventario = float((inventario[L.COL_I_STOCK] * inventario[L.COL_I_COSTO]).sum())

c1, c2, c3, c4 = st.columns(4)
with c1:
    ui.kpi_card("Materiales", f"{len(inventario)}", "🧵", ui.COLORES["violeta"])
with c2:
    ui.kpi_card("Stock total", f"{stock_total:,.0f} m²", "📦", ui.COLORES["azul"])
with c3:
    ui.kpi_card("En stock crítico", f"{len(criticos)}", "⚠️", ui.COLORES["rojo"])
with c4:
    ui.kpi_card("Valor del inventario", f"S/ {valor_inventario:,.0f}", "💰", ui.COLORES["verde"])

st.write("")

# ---------------------------------------------------------------------------
# Alerta visual de stock crítico
# ---------------------------------------------------------------------------
if not criticos.empty:
    items = []
    for _, r in criticos.iterrows():
        items.append(
            f"<li><b>{r[L.COL_I_TIPO_CUERO]} · {r[L.COL_I_COLOR]}</b> — "
            f"stock {r[L.COL_I_STOCK]:,.0f} m² (mínimo {r[L.COL_I_STOCK_MIN]:,.0f} m²)</li>"
        )
    st.markdown(
        f"""
        <div style="background:#FEECEC;border:1.5px solid #F5B5B7;border-radius:14px;
                    padding:14px 20px;color:#9B1C1F;">
            <div style="font-weight:800;font-size:15px;">⚠️ Alerta: {len(criticos)} material(es) en stock crítico</div>
            <ul style="margin:8px 0 0 0;padding-left:20px;font-size:14px;">{''.join(items)}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.success("Todos los materiales están por encima de su stock mínimo. 👍", icon="✅")

st.write("")

# ---------------------------------------------------------------------------
# Tabla de inventario con barra de progreso de stock
# ---------------------------------------------------------------------------
st.markdown("#### Detalle del inventario")
vista = inventario.copy()
vista_max = float(vista[L.COL_I_STOCK].max()) if len(vista) else 1.0
st.dataframe(
    vista,
    use_container_width=True,
    hide_index=True,
    column_config={
        L.COL_I_STOCK: st.column_config.ProgressColumn(
            "Stock actual", format="%.0f m²", min_value=0, max_value=vista_max
        ),
        L.COL_I_STOCK_MIN: st.column_config.NumberColumn(format="%.0f m²"),
        L.COL_I_COSTO: st.column_config.NumberColumn(format="S/ %.2f"),
    },
)

st.divider()

# ---------------------------------------------------------------------------
# Registrar movimiento (entrada / salida)
# ---------------------------------------------------------------------------
col_form, col_min = st.columns(2)

with col_form:
    st.markdown("#### 🔄 Registrar movimiento")
    etiquetas = {
        f"{r[L.COL_I_CODIGO]} · {r[L.COL_I_TIPO_CUERO]} · {r[L.COL_I_COLOR]}": r[L.COL_I_CODIGO]
        for _, r in inventario.iterrows()
    }
    with st.form("movimiento", clear_on_submit=True):
        sel = st.selectbox("Material", list(etiquetas.keys()))
        tipo_mov = st.radio("Tipo de movimiento", ["Entrada", "Salida"], horizontal=True)
        cantidad = st.number_input("Cantidad (m²)", min_value=0.0, value=50.0, step=10.0)
        guardar_mov = st.form_submit_button("Registrar movimiento", type="primary",
                                            use_container_width=True)

    if guardar_mov:
        codigo = etiquetas[sel]
        idx = inventario.index[inventario[L.COL_I_CODIGO] == codigo][0]
        stock_actual = float(inventario.at[idx, L.COL_I_STOCK])
        if tipo_mov == "Salida" and cantidad > stock_actual:
            st.error(
                f"No puedes retirar {cantidad:,.0f} m²: solo hay "
                f"{stock_actual:,.0f} m² disponibles."
            )
        else:
            nuevo = stock_actual + cantidad if tipo_mov == "Entrada" else stock_actual - cantidad
            df = L.cargar_inventario()
            df.at[idx, L.COL_I_STOCK] = nuevo
            # Recalcular estado para que persista en el Excel
            df[L.COL_I_ESTADO] = df.apply(
                lambda r: "Crítico" if r[L.COL_I_STOCK] < r[L.COL_I_STOCK_MIN] else "OK", axis=1
            )
            L.guardar_hoja(L.HOJA_INVENTARIO, df)
            st.success(
                f"{tipo_mov} de {cantidad:,.0f} m² registrada. "
                f"Nuevo stock de {sel}: **{nuevo:,.0f} m²**.",
                icon="✅",
            )
            st.rerun()

with col_min:
    st.markdown("#### 🎚️ Ajustar stock mínimo")
    etiquetas2 = {
        f"{r[L.COL_I_CODIGO]} · {r[L.COL_I_TIPO_CUERO]} · {r[L.COL_I_COLOR]}": r[L.COL_I_CODIGO]
        for _, r in inventario.iterrows()
    }
    with st.form("ajuste_min", clear_on_submit=True):
        sel2 = st.selectbox("Material", list(etiquetas2.keys()), key="min_sel")
        cod2 = etiquetas2[sel2]
        actual_min = float(inventario.loc[inventario[L.COL_I_CODIGO] == cod2, L.COL_I_STOCK_MIN].iloc[0])
        nuevo_min = st.number_input("Nuevo stock mínimo (m²)", min_value=0.0,
                                    value=actual_min, step=10.0)
        guardar_min = st.form_submit_button("Actualizar mínimo", use_container_width=True)

    if guardar_min:
        df = L.cargar_inventario()
        idx2 = df.index[df[L.COL_I_CODIGO] == cod2][0]
        df.at[idx2, L.COL_I_STOCK_MIN] = nuevo_min
        df[L.COL_I_ESTADO] = df.apply(
            lambda r: "Crítico" if r[L.COL_I_STOCK] < r[L.COL_I_STOCK_MIN] else "OK", axis=1
        )
        L.guardar_hoja(L.HOJA_INVENTARIO, df)
        st.success(f"Stock mínimo de {sel2} actualizado a **{nuevo_min:,.0f} m²**.", icon="✅")
        st.rerun()
