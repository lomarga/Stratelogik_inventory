# Sistema de Inteligencia y Optimización de Inventarios | Stratelogik

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://stratelogik.com/)

Este repositorio contiene el código fuente de la **Control Tower de Inventarios**, una plataforma analítica desarrollada por **Stratelogik**. Está diseñada para transformar datos transaccionales históricos en estrategias operativas claras, permitiendo a los equipos de Supply Chain y S&OP tomar decisiones basadas en modelos estocásticos y segmentación avanzada.

## Arquitectura de la Plataforma

La aplicación está dividida en tres módulos analíticos principales:

### 1. Segmentación de Portafolio (Matriz ABC-XYZ)
Clasificación dinámica de todos los SKUs de la operación cruzando el volumen de demanda (Pareto ABC) con la predictibilidad y volatilidad del mercado (Coeficiente de Variación XYZ).
* **Dispersión Visual:** Gráfico interactivo que distribuye los productos en 9 cuadrantes de riesgo.
* **Guía Estratégica:** Recomendaciones operativas automatizadas (políticas de ROP, niveles de revisión y mitigación de riesgo) según el cuadrante del producto.

### 2. Simulación de Escenarios y Alertas (What-If)
Motor de cálculo táctico para la prevención de quiebres de stock y mitigación de capital inmovilizado.
* **Radiografía del Almacén:** Mapa de calor (Treemap) que evalúa la salud de todo el portafolio en una fecha de corte, identificando excesos de inventario y riesgos de desabastecimiento.
* **Proyección Estocástica a 90 Días:** Simulación individual por SKU que calcula y grafica en tiempo real el Punto de Reorden (ROP), el Stock de Seguridad y el Nivel Máximo (Target Stock) basándose en el Lead Time y los Días de Cobertura requeridos.

### 3. Glosario Analítico
Diccionario técnico integrado en la plataforma para alinear conceptos estadísticos (Nivel de Servicio, CV, ROP) con el equipo operativo y directivo del cliente.

## Requisitos Técnicos e Instalación Local

El entorno requiere Python 3.10 o superior. Para ejecutar la plataforma en un entorno local:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/nombre-del-repo.git](https://github.com/tu-usuario/nombre-del-repo.git)
   cd nombre-del-repo
