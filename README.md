# 🤖 Agente de Optimización de Inventarios | Stratelogik

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://stratelogik.com/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Este repositorio contiene el código fuente del **Agente de IA para Optimización de Inventarios**, una herramienta interactiva diseñada por **Stratelogik** para facilitar la toma de decisiones tácticas en procesos de S&OP (Sales and Operations Planning) y gestión de redes de distribución.

## 🎯 Objetivo del Proyecto

En entornos logísticos y de manufactura, planificar basándose únicamente en la "demanda promedio" expone a la operación a roturas de stock o excesos de capital inmovilizado. Esta aplicación demuestra cómo la analítica avanzada puede calcular dinámicamente parámetros críticos en tiempo real, adaptándose a la volatilidad del mercado y a las variaciones en los tiempos de entrega (Lead Time).

## ✨ Características Principales

* **Cálculo Dinámico del ROP:** Actualización instantánea del Punto de Reorden óptimo mediante modelos estadísticos.
* **Sensing de Volatilidad:** Dimensionamiento automático del Stock de Seguridad basado en Z-Scores y desviaciones estándar.
* **Simulación a 90 Días:** Motor de simulación estocástica que proyecta el comportamiento del inventario y los ciclos de reabastecimiento (Generado con Plotly).
* **Impacto Financiero:** Cuantificación en tiempo real del capital inmovilizado en función del nivel de servicio objetivo y el costo unitario del producto.
* **Interfaz Corporativa:** Diseño de alto contraste (Dark Mode) optimizado para presentaciones ejecutivas y visibilidad en centros de control.

## 🛠️ Tecnologías Utilizadas

* **Framework Web:** [Streamlit](https://streamlit.io/)
* **Análisis Numérico:** NumPy, Pandas, SciPy (Estadística)
* **Visualización de Datos:** Plotly Graph Objects

## 🚀 Instalación y Uso Local

Para ejecutar este dashboard en un entorno local, sigue estos pasos:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/nombre-del-repo.git](https://github.com/tu-usuario/nombre-del-repo.git)
   cd nombre-del-repo