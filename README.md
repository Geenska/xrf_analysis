# 🔬 XRF Analyzer Pro - CNCPC

> **Procesamiento Masivo e Interpretación de Espectros XRF para Pigmentos Históricos y Materiales Arqueológicos**

![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

**XRF Analyzer Pro** es una aplicación de escritorio diseñada para la visualización, calibración, sustracción de fondo continuo, identificación elemental y análisis estadístico multivariado de espectros de Fluorescencia de Rayos X (XRF), con un enfoque especializado en el estudio no destructivo del patrimonio cultural, obras de arte y materiales arqueológicos.

---

## 🌟 Características Principales

* 📊 **Visualización Espectral Interactiva:**
  * Representación en kilo-electronvoltios ($\text{keV}$) contra conteos o tasa de conteos ($\text{CPS}$).
  * Marcado automático e interactivo de líneas de emisión caracteristicas ($K\alpha$, $K\beta$, $L\alpha$, $L\beta$, $M\alpha$).
  * Control flexible de rango de energía ($16\text{ keV}$, $30\text{ keV}$, $40\text{ keV}$ o manual) y etiquetas flotantes sobre picos.

* 🧹 **Sustracción de Fondo y Búsqueda de Picos:**
  * Algoritmo **SNIP** (*Statistics-sensitive Non-linear Iterative Peak-clipping*) para la estimación y remoción del fondo continuo de bremsstrahlung.
  * Identificación adaptativa de picos basada en estadísticas de ruido Poisson ($\ge 3\sqrt{N}$).
  * Integración de áreas brutas y áreas netas por pico.

* 🧪 **Identificación de Pigmentos Históricos y Compuestos:**
  * Base de datos arqueométrica integrada para la interpretación automática de pigmentos (Bermellón, Verde Esmeralda, Ocres de Hierro, Blanco de Plomo, Plomo-Estaño, Azurita/Malaquita, etc.).
  * Estimación porcentual aproximada de fases minerales (Yeso $\text{CaSO}_4$, Calcita $\text{CaCO}_3$, Hematita/Goethita).

* 📈 **Análisis Estadístico Multivariado (PCA):**
  * Análisis de Componentes Principales (PCA) mediante SVD sobre matrices de covarianza y correlación para agrupación y diferenciación de muestras espectrales.

* 📁 **Gestión de Proyectos y Árbol de Archivos:**
  * Carga por arrastrar y soltar (*Drag & Drop*) de archivos individuales o estructuras completas de directorios.
  * Cálculo y visualización automática del espectro **SUMA** por carpeta o grupo.

---

## 📁 Formatos de Archivo Soportados

| Formato | Descripción | Software / Origen |
| :--- | :--- | :--- |
| **`.pdz`** | Espectros binarios XRF de mano | Bruker Tracer III / IV / 5i |
| **`.rtx`** / **`.rrtx`** | Proyectos y sesiones en formato XML | Bruker ARTAX |
| **Directorios** | Estructuras de carpetas locales o remotas | Sistema de Archivos |

---

## 📑 Opciones de Exportación

La aplicación ofrece múltiples modalidades para exportar y compartir datos procesados:

1. **🎯 Exportación ARTAX con Líneas Seleccionadas (`todos.xls` / `.xlsx`):**
   * Genera un reporte compatible con Bruker ARTAX con las pestañas estándar `Parameter` y `Points`.
   * Incluye únicamente los espectros individuales (excluyendo automáticamente las sumas) y filtra únicamente las columnas de los elementos marcados en la lista de líneas de referencia.
   * Limpia y estandariza los nombres de las muestras (ej. `ANALYZE_EMP-7060`).

2. **📊 Exportación Excel Universal:**
   * Reporte consolidado con metadatos, áreas netas, conteos totales e interpretación elemental de todas las muestras cargadas.

3. **📈 Exportación con Gráficas por Hoja:**
   * Archivo Excel interactivo con pestañas individuales por muestra y gráficos de alta resolución integrados.

4. **💾 Proyecto Bruker ARTAX (`.rtx`):**
   * Guarda el estado completo de la sesión y avances del análisis en un archivo XML compatible con software comercial ARTAX.

5. **📥 Exportación para Software PAST:**
   * Exporta la matriz de espectros y elementos con etiquetas de filas/columnas formateadas para análisis estadístico paleontológico/arqueológico en **PAST**.

---

## 🚀 Instalación y Uso

### Opción 1: Windows (Iniciador Rápido)
Simplemente haz doble clic en el archivo script **`run_xrf.bat`**.  
El instalador verificará Python, creará el entorno virtual e instalará las dependencias necesarias de forma automática.

### Opción 2: Linux / macOS (Línea de Comandos)

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Geenska/xrf_analysis.git
   cd xrf_analysis
   ```

2. **Crear y activar entorno virtual:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
   *(En sistemas Linux basados en Debian/Ubuntu, asegúrate de contar con `python3-tk`: `sudo apt install python3-tk`)*.

4. **Ejecutar la aplicación:**
   ```bash
   python xrf_analysis.py
   ```

---

## 🧪 Pruebas Unitarias

El proyecto incluye una suite de pruebas automatizadas para verificar el motor de cálculo y la calibración espectral:

```bash
python test_analysis.py
```

---

## 🏛️ Créditos e Institución

Desarrollado para el **Laboratorio CÓDICE** y la **CNCPC** (Coordinación Nacional de Conservación del Patrimonio Cultural - INAH) para el procesamiento masivo, análisis espectral no destructivo e interpretación de pigmentos históricos en bienes culturales.
