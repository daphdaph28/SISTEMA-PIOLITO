# -*- coding: utf-8 -*-
"""
2_Chatbot.py — Asistente de consumo de cuero
============================================
El usuario escribe preguntas en lenguaje natural, por ejemplo:

    "¿Cuánto cuero necesito para fabricar 500 pares del modelo BP-001?"
    "Necesito 1200 pares de TL-003"

El asistente interpreta la pregunta (sin IA externa ni APIs: solo Pandas +
reglas) y responde con el detalle del consumo, el stock y la recomendacion
de compra. Toda la informacion se consulta desde el Excel.
"""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import loader as L
from utils import calculadora as C
from utils import ui

st.set_page_config(page_title="Chatbot · Piolito", page_icon="💬", layout="wide")
ui.aplicar_estilos()
ui.marca_sidebar()

modelos = L.cargar_modelos()
inventario = L.cargar_inventario()

ui.encabezado("Chatbot de consumo de cuero",
              "Pregunta en lenguaje natural cuánto cuero necesitas para un pedido.")

# ---------------------------------------------------------------------------
# Estado de la conversacion
# ---------------------------------------------------------------------------
if "chat" not in st.session_state:
    st.session_state.chat = [
        {
            "rol": "bot",
            "texto": (
                "¡Hola! 👋 Soy tu asistente de planificación de cuero. "
                "Escríbeme algo como: *“¿Cuánto cuero necesito para fabricar "
                "500 pares del modelo BP-001?”*"
            ),
        }
    ]


def responder(pregunta):
    """Procesa la pregunta del usuario y agrega la respuesta del bot al chat."""
    st.session_state.chat.append({"rol": "user", "texto": pregunta})
    resultado = C.interpretar_pregunta(pregunta, modelos, inventario)
    st.session_state.chat.append({"rol": "bot", "resultado": resultado, "texto": pregunta})


# ---------------------------------------------------------------------------
# Sugerencias rapidas (usan modelos REALES del Excel)
# ---------------------------------------------------------------------------
st.markdown("##### Ejemplos rápidos")
ejemplos = []
codigos_demo = modelos[L.COL_M_CODIGO].head(3).tolist()
cantidades_demo = [500, 1200, 800]
for cod, cant in zip(codigos_demo, cantidades_demo):
    ejemplos.append(f"¿Cuánto cuero necesito para fabricar {cant} pares del modelo {cod}?")

cols = st.columns(len(ejemplos)) if ejemplos else []
for col, ej in zip(cols, ejemplos):
    with col:
        if st.button(ej, use_container_width=True, key="ej_" + ej):
            responder(ej)

st.divider()

# ---------------------------------------------------------------------------
# Render de la respuesta del bot
# ---------------------------------------------------------------------------


def render_resultado(res):
    """Dibuja la tarjeta profesional de respuesta segun el resultado."""
    # --- Casos de error / aclaracion ---
    if res.get("error") == "modelo_no_encontrado":
        disponibles = ", ".join(modelos[L.COL_M_CODIGO].head(12).tolist())
        st.warning(
            f"No encontré ese modelo en la base de datos. "
            f"Prueba con un código válido, por ejemplo: **{disponibles}** …"
        )
        return
    if res.get("error") == "sin_cantidad":
        st.warning(
            f"Detecté el modelo **{res.get('codigo')}**, pero no entendí la "
            f"cantidad de pares. Indícame un número, por ejemplo: *“500 pares”*."
        )
        return
    if res.get("error"):
        st.warning("No entendí la pregunta. Indícame el **modelo** y la **cantidad de pares**.")
        return

    # --- Respuesta correcta ---
    suficiente = res["suficiente"]
    estado_color = ui.COLORES["verde"] if suficiente else ui.COLORES["rojo"]
    estado_txt = "Stock suficiente ✅" if suficiente else "Stock insuficiente ⚠️"

    st.markdown(
        f"""
        <div style="background:#FFFFFF;border:1.5px solid #E8EAF0;border-radius:16px;
                    padding:18px 22px;box-shadow:0 4px 14px rgba(26,40,68,0.06);">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="font-size:17px;font-weight:800;color:#1A2844;">
                    {res['codigo']} · {res['categoria']}
                </div>
                <span class="pill" style="background:{ui._tint(estado_color)};color:{estado_color};">
                    {estado_txt}
                </span>
            </div>
            <div style="color:#64748B;font-size:13px;margin-top:2px;">
                Temporada: {res['temporada']} · Material: {res['material']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    c1, c2, c3 = st.columns(3)
    with c1:
        ui.kpi_card("Cantidad solicitada", f"{res['cantidad_pares']:,} pares", "👟",
                    ui.COLORES["violeta"])
    with c2:
        ui.kpi_card("Consumo por par", f"{res['consumo_por_par']:.2f} m²", "📏",
                    ui.COLORES["azul"])
    with c3:
        ui.kpi_card("Consumo total requerido", f"{res['consumo_total']:,.2f} m²", "🧵",
                    ui.COLORES["ambar"])

    st.write("")
    c4, c5, c6 = st.columns(3)
    with c4:
        ui.kpi_card("Stock disponible", f"{res['stock_disponible']:,.2f} m²", "📦",
                    ui.COLORES["azul"])
    with c5:
        color_rest = ui.COLORES["verde"] if res["stock_restante"] >= 0 else ui.COLORES["rojo"]
        ui.kpi_card("Stock restante", f"{res['stock_restante']:,.2f} m²", "📉", color_rest)
    with c6:
        if res["comprar"]:
            ui.kpi_card("Compra sugerida", f"{res['sugerido_compra']:,.2f} m²", "🛒",
                        ui.COLORES["rojo"], f"≈ S/ {res['costo_compra_estimado']:,.2f}")
        else:
            ui.kpi_card("Compra sugerida", "No requerida", "🛒", ui.COLORES["verde"],
                        "el inventario alcanza")

    # Conclusion en texto
    st.write("")
    if suficiente:
        st.success(
            f"**Conclusión:** el inventario es suficiente para fabricar "
            f"{res['cantidad_pares']:,} pares del modelo {res['codigo']}. "
            f"Quedarían **{res['stock_restante']:,.2f} m²** de {res['material']}.",
            icon="✅",
        )
    else:
        st.error(
            f"**Conclusión:** el inventario NO alcanza. Faltan "
            f"**{res['faltante']:,.2f} m²** de {res['material']}. "
            f"Se recomienda comprar **{res['sugerido_compra']:,.2f} m²** "
            f"(≈ S/ {res['costo_compra_estimado']:,.2f}).",
            icon="⚠️",
        )


# ---------------------------------------------------------------------------
# Historial de conversacion
# ---------------------------------------------------------------------------
for msg in st.session_state.chat:
    if msg["rol"] == "user":
        with st.chat_message("user", avatar="🧑‍🏭"):
            st.markdown(msg["texto"])
    else:
        with st.chat_message("assistant", avatar="🤖"):
            if "resultado" in msg:
                render_resultado(msg["resultado"])
            else:
                st.markdown(msg["texto"])

# ---------------------------------------------------------------------------
# Entrada de chat
# ---------------------------------------------------------------------------
pregunta = st.chat_input("Escribe tu pregunta… (ej. 500 pares del modelo BP-001)")
if pregunta:
    responder(pregunta)
    st.rerun()
