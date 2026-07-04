# ProyectoCRMTelecom


# Sistema CRM de Telecomunicaciones

Sistema integral de Gestión de Relación con Clientes (CRM) para operadoras de telecomunicaciones, desarrollado con Python y Flask. Incluye un módulo analítico para la predicción del riesgo de abandono (Churn) basado en el historial de consumo.

## Características Principales
* **Gestión de Usuarios:** Registro y asignación de planes (Postpago, Prepago, Fibra Óptica).
* **Facturación Automatizada:** Cálculo dinámico con consumo de API en tiempo real para tipo de cambio (USD a PEN).
* **Predicción de Churn:** Algoritmo continuo basado en la caída del consumo histórico.
* **Dashboard Analítico:** Gráficos integrados generados con Pandas y Matplotlib.

## Tecnologías Utilizadas
* **Backend:** Python, Flask, SQLAlchemy
* **Ciencia de Datos:** Pandas, NumPy, Matplotlib, Seaborn
* **Frontend:** HTML5, Bootstrap 5, Jinja2
* **Testing:** Unittest

## Instalación y Ejecución
1. Clonar el repositorio:
   `git clone https://github.com/tu-usuario/telecom-crm.git`
2. Instalar las dependencias:
   `pip install -r requirements.txt`
3. Ejecutar la aplicación:
   `python app.py`
