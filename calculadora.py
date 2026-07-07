# -*- coding: utf-8 -*-
"""
calculadora.py
--------------
Logica de negocio del sistema Piolito.

Aqui vive todo el "cerebro" del planificador de consumo de cuero:

  * Calcular el consumo de cuero requerido para X pares de un modelo.
  * Encontrar el material de inventario que usa cada modelo
    (se cruza por Tipo de cuero + Color).
  * Evaluar si el stock alcanza o si hay que comprar mas cuero.
  * Interpretar preguntas en lenguaje natural del chatbot
    (sin IA externa: solo Pandas + reglas).

Ninguna funcion de este modulo usa APIs externas ni modelos de IA.
"""

import re
import unicodedata

import pandas as pd

from utils import loader as L


# ---------------------------------------------------------------------------
# Helpers de texto
# ---------------------------------------------------------------------------


def _normalizar(texto):
    """Pasa a minusculas y quita acentos para comparar de forma flexible."""
    if texto is None:
        return ""
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto


# ---------------------------------------------------------------------------
# Calculo de consumo
# ---------------------------------------------------------------------------


def consumo_requerido(consumo_por_par, cantidad_pares):
    """Consumo total de cuero (m²) = consumo por par * cantidad de pares."""
    try:
        return round(float(consumo_por_par) * float(cantidad_pares), 2)
    except (TypeError, ValueError):
        return 0.0


def material_de_modelo(modelo_row, inventario_df):
    """Devuelve la fila de inventario que corresponde a un modelo.

    El cruce se hace por Tipo de cuero + Color (un modelo de cuero vacuno
    color negro consume el material de inventario 'Cuero Vacuno / Negro').

    Retorna una Serie de Pandas o None si no hay coincidencia.
    """
    tipo = _normalizar(modelo_row.get(L.COL_M_TIPO_CUERO))
    color = _normalizar(modelo_row.get(L.COL_M_COLOR))

    for _, inv in inventario_df.iterrows():
        if (
            _normalizar(inv.get(L.COL_I_TIPO_CUERO)) == tipo
            and _normalizar(inv.get(L.COL_I_COLOR)) == color
        ):
            return inv

    # Si no hay coincidencia exacta de color, intentar solo por tipo de cuero
    candidatos = inventario_df[
        inventario_df[L.COL_I_TIPO_CUERO].apply(_normalizar) == tipo
    ]
    if not candidatos.empty:
        return candidatos.iloc[0]

    return None


def evaluar_consumo(codigo_o_nombre, cantidad_pares, modelos_df=None, inventario_df=None):
    """Evalua un pedido de fabricacion y devuelve un diccionario completo.

    Parametros
    ----------
    codigo_o_nombre : str   -> codigo (BP-001) o nombre del modelo
    cantidad_pares  : int   -> pares a fabricar
    modelos_df      : DataFrame opcional (se carga si no se pasa)
    inventario_df   : DataFrame opcional (se carga si no se pasa)

    Devuelve un dict con todas las claves que la UI necesita, o
    {"error": "..."} si el modelo no se encuentra.
    """
    if modelos_df is None:
        modelos_df = L.cargar_modelos()
    if inventario_df is None:
        inventario_df = L.cargar_inventario()

    modelo_row = buscar_modelo(codigo_o_nombre, modelos_df)
    if modelo_row is None:
        return {"error": "modelo_no_encontrado", "consulta": codigo_o_nombre}

    consumo_par = float(modelo_row.get(L.COL_M_CONSUMO) or 0)
    total = consumo_requerido(consumo_par, cantidad_pares)

    inv = material_de_modelo(modelo_row, inventario_df)
    if inv is None:
        material = f"{modelo_row.get(L.COL_M_TIPO_CUERO)} / {modelo_row.get(L.COL_M_COLOR)}"
        stock_disp = 0.0
        costo = 0.0
    else:
        material = f"{inv.get(L.COL_I_TIPO_CUERO)} / {inv.get(L.COL_I_COLOR)}"
        stock_disp = float(inv.get(L.COL_I_STOCK) or 0)
        costo = float(inv.get(L.COL_I_COSTO) or 0)

    suficiente = stock_disp >= total
    faltante = max(0.0, round(total - stock_disp, 2))
    # Sugerencia de compra: lo que falta + 10% de colchon de seguridad
    sugerido_compra = round(faltante * 1.10, 2) if faltante > 0 else 0.0
    costo_compra = round(sugerido_compra * costo, 2)
    stock_restante = round(stock_disp - total, 2)

    return {
        "error": None,
        "codigo": modelo_row.get(L.COL_M_CODIGO),
        "modelo": modelo_row.get(L.COL_M_MODELO),
        "categoria": modelo_row.get(L.COL_M_CATEGORIA),
        "temporada": modelo_row.get(L.COL_M_TEMPORADA),
        "cantidad_pares": int(cantidad_pares),
        "consumo_por_par": round(consumo_par, 3),
        "consumo_total": total,
        "material": material,
        "stock_disponible": round(stock_disp, 2),
        "stock_restante": stock_restante,
        "suficiente": suficiente,
        "faltante": faltante,
        "comprar": not suficiente,
        "sugerido_compra": sugerido_compra,
        "costo_por_m2": costo,
        "costo_compra_estimado": costo_compra,
    }


# ---------------------------------------------------------------------------
# Busqueda de modelos
# ---------------------------------------------------------------------------


def buscar_modelo(consulta, modelos_df):
    """Busca un modelo por codigo o nombre dentro del DataFrame de modelos.

    Prioridad de coincidencia:
      1. Codigo exacto (BP-001)
      2. Nombre de modelo exacto
      3. Codigo / nombre contenido dentro del texto
    Devuelve la fila (Serie) o None.
    """
    q = _normalizar(consulta)
    if not q:
        return None

    codigos = modelos_df[L.COL_M_CODIGO].apply(_normalizar)
    nombres = modelos_df[L.COL_M_MODELO].apply(_normalizar)

    # 1. Codigo exacto
    exacto = modelos_df[codigos == q]
    if not exacto.empty:
        return exacto.iloc[0]

    # 2. Nombre exacto
    exacto = modelos_df[nombres == q]
    if not exacto.empty:
        return exacto.iloc[0]

    # 3. Coincidencia parcial (el codigo/nombre aparece dentro de la consulta)
    for idx, fila in modelos_df.iterrows():
        cod = _normalizar(fila.get(L.COL_M_CODIGO))
        nom = _normalizar(fila.get(L.COL_M_MODELO))
        if cod and cod in q:
            return fila
        if nom and nom in q:
            return fila

    return None


# ---------------------------------------------------------------------------
# Interpretacion de preguntas del chatbot (parser de lenguaje natural simple)
# ---------------------------------------------------------------------------


def interpretar_pregunta(texto, modelos_df=None, inventario_df=None):
    """Interpreta una pregunta libre del usuario y devuelve la evaluacion.

    Ejemplos que entiende:
      "¿Cuánto cuero necesito para fabricar 500 pares del modelo BP-001?"
      "Necesito 1200 pares de TL-003"
      "consumo de 300 BP-005"

    Estrategia (sin IA): extraer el primer numero como cantidad de pares y
    detectar el codigo/nombre de modelo presente en el texto.

    Devuelve el mismo dict que evaluar_consumo(), o un dict de error con
    una pista para el usuario.
    """
    if modelos_df is None:
        modelos_df = L.cargar_modelos()
    if inventario_df is None:
        inventario_df = L.cargar_inventario()

    if not texto or not texto.strip():
        return {"error": "vacio"}

    # 1. Extraer la cantidad de pares (primer numero entero del texto)
    numeros = re.findall(r"\d[\d.,]*", texto)
    cantidad = None
    for n in numeros:
        limpio = n.replace(".", "").replace(",", "")
        if limpio.isdigit():
            cantidad = int(limpio)
            break

    # 2. Detectar el modelo: primero por codigo tipo XX-000, luego por nombre
    modelo_row = None
    patron_codigo = re.search(r"[A-Za-z]{2,4}\s*-\s*\d{1,4}", texto)
    if patron_codigo:
        codigo = patron_codigo.group(0).replace(" ", "").upper()
        modelo_row = buscar_modelo(codigo, modelos_df)

    if modelo_row is None:
        # Buscar cualquier codigo/nombre de modelo contenido en el texto
        modelo_row = buscar_modelo(texto, modelos_df)

    # 3. Validar y responder
    if modelo_row is None:
        return {
            "error": "modelo_no_encontrado",
            "consulta": texto,
            "cantidad": cantidad,
        }
    if cantidad is None or cantidad <= 0:
        return {
            "error": "sin_cantidad",
            "consulta": texto,
            "codigo": modelo_row.get(L.COL_M_CODIGO),
        }

    return evaluar_consumo(
        modelo_row.get(L.COL_M_CODIGO),
        cantidad,
        modelos_df=modelos_df,
        inventario_df=inventario_df,
    )
