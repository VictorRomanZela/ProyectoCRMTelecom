import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import io

def _clients_to_dataframe(clients) -> pd.DataFrame:
    """Transforma los objetos, limpia los datos y realiza cruces (Merge)."""
    data = []
    for c in clients:
        history = c.consumption_history.get('data_usage_history_gb', [])
        
        # Si no hay historial, np.mean devolvería NaN (Not a Number)
        avg_usage = np.mean(history) if history else np.nan
        
        data.append({
            'ID': c.client_id,
            'Nombre': c.name,
            'Plan_ID': c.current_plan.name,
            'Riesgo_Churn': c.get_churn_risk(),
            'Consumo_Promedio': avg_usage
        })
        
    df_clientes = pd.DataFrame(data)
    
    if df_clientes.empty:
        return df_clientes

    # --- 1. LIMPIEZA DE DATOS (Pandas) ---
    # Reemplazamos los valores nulos (NaN) con 0.0 para que las gráficas no fallen
    df_clientes['Consumo_Promedio'] = df_clientes['Consumo_Promedio'].fillna(0.0)
    
    # --- 2. USO DE MERGE (Pandas) ---
    # Simulamos un DataFrame secundario con detalles técnicos de la red
    datos_red = {
        'Plan_ID': ['Básico', 'Premium', 'Mensual', 'Fibra 100', 'Fibra 500'],
        'Tecnologia': ['4G LTE', '5G', '4G LTE', 'FTTH', 'FTTH']
    }
    df_red = pd.DataFrame(datos_red)
    
    # Unimos la información del cliente con la tecnología de su plan (Left Join)
    df_final = pd.merge(df_clientes, df_red, on='Plan_ID', how='left')
    
    return df_final

def generate_advanced_dashboard(clients):
    """Genera una imagen con múltiples gráficas (Subplots)."""
    df = _clients_to_dataframe(clients)
    
    # --- 3. SUBPLOTS (Matplotlib) ---
    # Creamos una figura grande con 1 fila y 2 columnas
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Aplicamos un estilo profesional general
    sns.set_theme(style="whitegrid")
    
    if not df.empty:
        # Gráfica 1 (Izquierda): Distribución de Churn
        sns.histplot(df['Riesgo_Churn'], bins=10, kde=True, color='#dc3545', ax=axes[0])
        axes[0].set_title('Distribución de Probabilidad de Churn', fontsize=14, fontweight='bold')
        axes[0].set_xlabel('Riesgo de Abandono (%)')
        axes[0].set_ylabel('Cantidad de Clientes')
        
        # --- 4. AGRUPACIÓN COMPLEJA (Groupby) ---
        # Agrupamos por tecnología para ver qué red consume más datos
        grouped_data = df.groupby('Tecnologia')['Consumo_Promedio'].mean().reset_index()
        
        # Gráfica 2 (Derecha): Consumo por Tecnología
        sns.barplot(data=grouped_data, x='Tecnologia', y='Consumo_Promedio', palette='mako', ax=axes[1])
        axes[1].set_title('Consumo Promedio por Tecnología de Red', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Tipo de Conexión')
        axes[1].set_ylabel('Consumo Promedio (GB)')
    else:
        axes[0].text(0.5, 0.5, 'Sin datos registrados', ha='center', va='center')
        axes[1].text(0.5, 0.5, 'Sin datos registrados', ha='center', va='center')

    # Ajustamos los márgenes para que no se superpongan los textos
    plt.tight_layout()
    
    # Guardamos en el buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100) # dpi=100 asegura buena calidad
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer
