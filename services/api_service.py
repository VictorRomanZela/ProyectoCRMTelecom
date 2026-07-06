import requests
from functools import lru_cache
from datetime import datetime  

@lru_cache(maxsize=1)
def obtener_tipo_cambio_usd_pen():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status() 
        datos = response.json()
        return datos['rates'].get('PEN', 3.75)
        
    except requests.RequestException as e:
        with open("log_errores.txt", "a", encoding="utf-8") as archivo_log:
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            mensaje_error = f"[{fecha_actual}] Fallo al conectar con la API: {str(e)}\n"
            archivo_log.write(mensaje_error)
            
        print("Error de red registrado en log_errores.txt")
        return 3.75
    
    