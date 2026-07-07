# 👟 Sistema de Planificación de Cuero — Piolito

Proyecto universitario para la empresa de **calzado infantil Piolito**.
Sistema sencillo, moderno e intuitivo (estilo Power BI) que ayuda a:

- **Planificar** el consumo de cuero según el modelo y la cantidad de pares.
- **Controlar** el inventario de cuero (entradas, salidas, alertas de stock).
- **Apoyar la toma de decisiones** con un dashboard, un chatbot y reportes.

> Toda la información proviene de **un único archivo Excel** (`data/Base_Piolito.xlsx`).
> **No se usa ninguna base de datos SQL** ni IA externa: el chatbot responde
> únicamente consultando el Excel con Pandas.

---

## 🧰 Tecnologías

- **Python**
- **Streamlit** — interfaz web
- **Pandas** — lectura y procesamiento de datos
- **Plotly** — gráficos interactivos
- **OpenPyXL** — lectura/escritura del Excel

---

## 📁 Estructura del proyecto

```
Proyecto_Piolito/
├── app.py                  # Página principal (inicio)
├── pages/
│   ├── 1_Dashboard.py      # KPIs + 6 gráficos interactivos
│   ├── 2_Chatbot.py        # Asistente de consumo de cuero
│   ├── 3_Modelos.py        # Catálogo + alta de modelos
│   ├── 4_Inventario.py     # Stock, movimientos y alertas
│   └── 5_Reportes.py       # Exportación a Excel
├── data/
│   └── Base_Piolito.xlsx   # Única fuente de datos
├── utils/
│   ├── loader.py           # Lectura/escritura del Excel
│   ├── calculadora.py      # Lógica de negocio + chatbot
│   └── ui.py               # Estilos y componentes visuales
├── .streamlit/
│   └── config.toml         # Tema visual
├── requirements.txt
└── README.md
```

---

## ▶️ Cómo ejecutar (Visual Studio Code)

1. **Abrir la carpeta** `Proyecto_Piolito` en Visual Studio Code.

2. **(Opcional pero recomendado) Crear un entorno virtual:**

   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Instalar las dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación:**

   ```bash
   streamlit run app.py
   ```

5. Se abrirá automáticamente en el navegador (normalmente `http://localhost:8501`).

---

## 🧭 Módulos

### 📊 1. Dashboard
Tarjetas KPI (total de modelos, stock total, stock disponible, materiales en
stock crítico, consumo total proyectado, consumo promedio por modelo) y **6
gráficos interactivos** con Plotly:
consumo por modelo, consumo por temporada, top modelos, stock por material,
estado del inventario y comparación stock vs. mínimo. Incluye **filtros** por
temporada y categoría.

### 💬 2. Chatbot de consumo de cuero
Escribe preguntas en lenguaje natural, por ejemplo:

> *¿Cuánto cuero necesito para fabricar 500 pares del modelo BP-001?*

El asistente interpreta la pregunta y responde con: modelo, cantidad
solicitada, consumo por par, consumo total requerido, material utilizado,
stock disponible, stock restante, si el stock es suficiente y, de no serlo,
la **cantidad sugerida de compra** (con su costo estimado).
*No usa IA externa: solo Pandas y reglas.*

### 👟 3. Modelos
Tabla interactiva con búsqueda y filtros. Permite **registrar nuevos modelos**,
que se guardan automáticamente en la hoja `MODELOS` del Excel.

### 📦 4. Inventario
Muestra el stock de cuero con barras de progreso, permite registrar
**entradas y salidas** y ajustar el **stock mínimo**. Cuando un material cae
por debajo del mínimo se muestra una **alerta visual automática**. Los cambios
se guardan en el Excel.

### 📑 5. Reportes
Exporta a **Excel** los reportes de inventario, consumo y modelos, además de un
**reporte consolidado** con todas las hojas.

---

## 📝 Notas

- El sistema lee y **escribe** sobre `data/Base_Piolito.xlsx`. Al guardar
  cambios (nuevos modelos, movimientos de inventario) el archivo se reescribe
  conservando todas las hojas; las *tablas con formato* de Excel pasan a ser
  rangos de datos normales.
- El formulario de modelos sigue el **esquema real** de la hoja `MODELOS`
  del Excel proporcionado.
- Los cálculos de consumo cruzan cada modelo con su material de inventario por
  **Tipo de cuero + Color**.

Proyecto desarrollado en Python con Streamlit · sin SQL · sin IA externa.
