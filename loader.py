# -*- coding: utf-8 -*-
"""
loader.py
---------
Capa de acceso a datos del sistema Piolito.

Toda la informacion del sistema vive en un unico archivo Excel
(data/Base_Piolito.xlsx). Este modulo se encarga de:

  * Leer cada hoja del Excel y devolverla como DataFrame de Pandas.
  * Limpiar / normalizar tipos de datos (numeros y fechas).
  * Guardar cambios de vuelta en el Excel conservando TODAS las hojas.

No se usa ninguna base de datos SQL: el Excel es la unica fuente de verdad.
"""

import os
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Rutas y nombres de hojas
# ---------------------------------------------------------------------------

# Carpeta /utils  ->  raiz del proyecto  ->  /data/Base_Piolito.xlsx
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCEL_PATH = os.path.join(BASE_DIR, "data", "Base_Piolito.xlsx")

# Nombres EXACTOS de las hojas dentro del Excel
HOJA_MODELOS = "MODELOS"
HOJA_INVENTARIO = "INVENTARIO_CUERO"
HOJA_PEDIDOS = "PEDIDOS"
HOJA_HISTORIAL = "HISTORIAL_CONSUMO"
HOJA_PROVEEDORES = "PROVEEDORES"

# ---------------------------------------------------------------------------
# Nombres de columnas (centralizados para evitar errores de tipeo)
# ---------------------------------------------------------------------------

# --- MODELOS ---
COL_M_CODIGO = "Código"
COL_M_MODELO = "Modelo"
COL_M_CATEGORIA = "Categoría"
COL_M_SUBCATEGORIA = "Subcategoría"
COL_M_GENERO = "Género"
COL_M_TEMPORADA = "Temporada"
COL_M_TIPO_CUERO = "Tipo de cuero"
COL_M_COLOR = "Color"
COL_M_TALLA_INI = "Talla inicial"
COL_M_TALLA_FIN = "Talla final"
COL_M_CONSUMO = "Consumo por par (m²)"
COL_M_PRECIO = "Precio venta S/"
COL_M_ESTADO = "Estado"

# --- INVENTARIO_CUERO ---
COL_I_CODIGO = "Código"
COL_I_TIPO_CUERO = "Tipo de cuero"
COL_I_COLOR = "Color"
COL_I_UNIDAD = "Unidad"
COL_I_STOCK = "Stock actual"
COL_I_STOCK_MIN = "Stock mínimo"
COL_I_COSTO = "Costo por m²"
COL_I_PROVEEDOR = "Proveedor"
COL_I_ESTADO = "Estado stock"

# --- PEDIDOS ---
COL_P_PEDIDO = "Pedido"
COL_P_FECHA = "Fecha"
COL_P_CLIENTE = "Cliente"
COL_P_COD_MODELO = "Código modelo"
COL_P_MODELO = "Modelo"
COL_P_CATEGORIA = "Categoría"
COL_P_PARES = "Cantidad de pares"
COL_P_CONSUMO = "Consumo requerido (m²)"
COL_P_STOCK_DISP = "Stock disponible (m²)"
COL_P_RESULTADO = "Resultado"
COL_P_ESTADO = "Estado"
COL_P_ENTREGA = "Fecha entrega estimada"

# --- HISTORIAL_CONSUMO ---
COL_H_FECHA = "Fecha"
COL_H_PEDIDO = "Pedido"
COL_H_COD_MODELO = "Código modelo"
COL_H_MODELO = "Modelo"
COL_H_PARES = "Pares fabricados"
COL_H_CONSUMO_TEO = "Consumo teórico (m²)"
COL_H_CONSUMO_REAL = "Consumo real (m²)"
COL_H_DIFERENCIA = "Diferencia (m²)"
COL_H_MERMA = "Merma %"
COL_H_OBS = "Observación"

# ---------------------------------------------------------------------------
# Utilidades internas
# ---------------------------------------------------------------------------


def _excel_serial_a_fecha(valor):
    """Convierte un numero de serie de Excel (ej. 46037) a datetime.

    Excel cuenta los dias desde el 30/12/1899. Si el valor ya es una fecha
    o no se puede convertir, se devuelve tal cual.
    """
    if pd.isna(valor):
        return valor
    if isinstance(valor, (datetime, pd.Timestamp)):
        return valor
    try:
        numero = float(valor)
        return datetime(1899, 12, 30) + timedelta(days=numero)
    except (ValueError, TypeError):
        return valor


def _a_numero(serie):
    """Convierte una columna a numerico de forma segura (NaN si no se puede)."""
    return pd.to_numeric(serie, errors="coerce")


# ---------------------------------------------------------------------------
# Lectura de hojas (con cache de Streamlit)
# ---------------------------------------------------------------------------
#
# Se usa st.cache_data para no releer el Excel en cada interaccion.
# La clave de cache incluye la fecha de modificacion del archivo, de modo
# que al guardar cambios el cache se invalida automaticamente.


def _mtime():
    """Marca de tiempo de modificacion del Excel (para invalidar el cache)."""
    try:
        return os.path.getmtime(EXCEL_PATH)
    except OSError:
        return 0.0


@st.cache_data(show_spinner=False)
def _leer_hoja(nombre_hoja, mtime_key):
    """Lee una hoja del Excel. mtime_key (fecha de modificación) fuerza la
    recarga automática cuando el archivo cambia, porque forma parte de la
    clave de cache."""
    df = pd.read_excel(EXCEL_PATH, sheet_name=nombre_hoja, engine="openpyxl")
    # Quitar columnas totalmente vacias que a veces deja Excel
    df = df.dropna(axis=1, how="all")
    # Quitar filas totalmente vacias
    df = df.dropna(axis=0, how="all").reset_index(drop=True)
    return df


def cargar_modelos():
    """Devuelve la hoja MODELOS con los numeros ya convertidos."""
    df = _leer_hoja(HOJA_MODELOS, _mtime()).copy()
    if COL_M_CONSUMO in df.columns:
        df[COL_M_CONSUMO] = _a_numero(df[COL_M_CONSUMO])
    if COL_M_PRECIO in df.columns:
        df[COL_M_PRECIO] = _a_numero(df[COL_M_PRECIO])
    return df


def cargar_inventario():
    """Devuelve la hoja INVENTARIO_CUERO con numeros convertidos y estado recalculado."""
    df = _leer_hoja(HOJA_INVENTARIO, _mtime()).copy()
    for col in (COL_I_STOCK, COL_I_STOCK_MIN, COL_I_COSTO):
        if col in df.columns:
            df[col] = _a_numero(df[col])
    # Recalcular el estado del stock segun los valores actuales
    if COL_I_STOCK in df.columns and COL_I_STOCK_MIN in df.columns:
        df[COL_I_ESTADO] = df.apply(
            lambda r: "Crítico" if r[COL_I_STOCK] < r[COL_I_STOCK_MIN] else "OK",
            axis=1,
        )
    return df


def cargar_pedidos():
    """Devuelve la hoja PEDIDOS con numeros y fechas convertidos."""
    df = _leer_hoja(HOJA_PEDIDOS, _mtime()).copy()
    for col in (COL_P_PARES, COL_P_CONSUMO, COL_P_STOCK_DISP):
        if col in df.columns:
            df[col] = _a_numero(df[col])
    for col in (COL_P_FECHA, COL_P_ENTREGA):
        if col in df.columns:
            df[col] = df[col].apply(_excel_serial_a_fecha)
    return df


def cargar_historial():
    """Devuelve la hoja HISTORIAL_CONSUMO con numeros y fechas convertidos."""
    df = _leer_hoja(HOJA_HISTORIAL, _mtime()).copy()
    for col in (
        COL_H_PARES,
        COL_H_CONSUMO_TEO,
        COL_H_CONSUMO_REAL,
        COL_H_DIFERENCIA,
        COL_H_MERMA,
    ):
        if col in df.columns:
            df[col] = _a_numero(df[col])
    if COL_H_FECHA in df.columns:
        df[COL_H_FECHA] = df[COL_H_FECHA].apply(_excel_serial_a_fecha)
    return df


def cargar_proveedores():
    """Devuelve la hoja PROVEEDORES."""
    return _leer_hoja(HOJA_PROVEEDORES, _mtime()).copy()


# ---------------------------------------------------------------------------
# Escritura de vuelta al Excel
# ---------------------------------------------------------------------------


def guardar_hoja(nombre_hoja, df_nuevo):
    """Guarda 'df_nuevo' en 'nombre_hoja' conservando el resto de hojas.

    Estrategia: se leen TODAS las hojas actuales, se reemplaza unicamente la
    hoja indicada y se reescribe el archivo completo. Asi nunca se pierden
    datos de las demas hojas.

    Tras guardar se limpia el cache para que la app muestre los datos frescos.
    """
    # 1. Leer todas las hojas tal como estan hoy
    hojas = pd.read_excel(EXCEL_PATH, sheet_name=None, engine="openpyxl")

    # 2. Reemplazar la hoja objetivo
    hojas[nombre_hoja] = df_nuevo

    # 3. Reescribir el archivo completo
    with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl") as writer:
        for nombre, df in hojas.items():
            df.to_excel(writer, sheet_name=nombre, index=False)

    # 4. Invalidar el cache de lectura
    st.cache_data.clear()


def excel_existe():
    """True si el archivo de datos esta disponible."""
    return os.path.exists(EXCEL_PATH)
