# -*- coding: utf-8 -*-
"""
5_Reportes.py — Exportación de reportes
=======================================
Permite descargar en formato Excel los reportes de:
  * Inventario de cuero
  * Consumo (historial de fabricación)
  * Modelos registrados
  * Reporte consolidado (todas las hojas en un solo archivo)

La generación se hace en memoria con Pandas + OpenPyXL.
"""

import io
import os
import sys
from datetime import datetime

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import loader as L
from utils import ui

st.set_page_config(page_title="Reportes · Piolito", page_icon="📑", layout="wide")
ui.aplicar_estilos()
ui.marca_sidebar()

modelos = L.cargar_modelos()
inventario = L.cargar_inventario()
pedidos = L.cargar_pedidos()
historial = L.cargar_historial()

ui.encabezado("Reportes", "Exporta la información del sistema a Excel.")


def a_excel(dfs_dict):
    """Convierte un dict {hoja: DataFrame} en bytes de un archivo .xlsx."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for hoja, df in dfs_dict.items():
            # Excel limita el nombre de hoja a 31 caracteres
            df.to_excel(writer, sheet_name=hoja[:31], index=False)
    buffer.seek(0)
    return buffer.getvalue()


hoy = datetime.now().strftime("%Y%m%d")

# ---------------------------------------------------------------------------
# Tarjetas de descarga
# ---------------------------------------------------------------------------
st.markdown("#### Descargas disponibles")
st.caption("Cada reporte se genera a partir de los datos actuales del Excel.")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        """
        <div style="background:#fff;border:1.5px solid #E8EAF0;border-radius:14px;padding:18px;">
            <div style="font-size:30px;">📦</div>
            <div style="font-weight:700;color:#1A2844;margin-top:6px;">Reporte de inventario</div>
            <div style="color:#64748B;font-size:13px;">Stock actual, mínimo, costo y estado.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.download_button(
        "⬇️ Descargar inventario",
        data=a_excel({"INVENTARIO_CUERO": inventario}),
        file_name=f"reporte_inventario_{hoy}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

with c2:
    st.markdown(
        """
        <div style="background:#fff;border:1.5px solid #E8EAF0;border-radius:14px;padding:18px;">
            <div style="font-size:30px;">🧵</div>
            <div style="font-weight:700;color:#1A2844;margin-top:6px;">Reporte de consumo</div>
            <div style="color:#64748B;font-size:13px;">Historial de consumo teórico y real.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.download_button(
        "⬇️ Descargar consumo",
        data=a_excel({"HISTORIAL_CONSUMO": historial, "PEDIDOS": pedidos}),
        file_name=f"reporte_consumo_{hoy}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

with c3:
    st.markdown(
        """
        <div style="background:#fff;border:1.5px solid #E8EAF0;border-radius:14px;padding:18px;">
            <div style="font-size:30px;">👟</div>
            <div style="font-weight:700;color:#1A2844;margin-top:6px;">Reporte de modelos</div>
            <div style="color:#64748B;font-size:13px;">Catálogo completo de modelos.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.download_button(
        "⬇️ Descargar modelos",
        data=a_excel({"MODELOS": modelos}),
        file_name=f"reporte_modelos_{hoy}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

st.write("")
st.divider()

# ---------------------------------------------------------------------------
# Reporte consolidado
# ---------------------------------------------------------------------------
st.markdown("#### 📚 Reporte consolidado")
st.caption("Un único archivo Excel con todas las hojas del sistema.")
st.download_button(
    "⬇️ Descargar reporte consolidado",
    data=a_excel({
        "MODELOS": modelos,
        "INVENTARIO_CUERO": inventario,
        "PEDIDOS": pedidos,
        "HISTORIAL_CONSUMO": historial,
    }),
    file_name=f"reporte_consolidado_piolito_{hoy}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    type="primary",
)

st.write("")

# ---------------------------------------------------------------------------
# Vista previa
# ---------------------------------------------------------------------------
st.markdown("#### Vista previa")
tab1, tab2, tab3 = st.tabs(["📦 Inventario", "🧵 Consumo", "👟 Modelos"])
with tab1:
    st.dataframe(inventario, use_container_width=True, hide_index=True)
with tab2:
    st.dataframe(historial, use_container_width=True, hide_index=True)
with tab3:
    st.dataframe(modelos, use_container_width=True, hide_index=True)
