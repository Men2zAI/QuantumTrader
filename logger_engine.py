import pandas as pd
import os
from datetime import datetime

def registrar_decision(ticker, precio, señal, fiabilidad):
    archivo = 'historial_decisiones.csv'
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    datos = {
        'fecha': [ahora],
        'ticker': [ticker],
        'precio_entrada': [precio],
        'prediccion': [señal],
        'fiabilidad': [f"{fiabilidad}%"],
        'resultado_real': ['PENDIENTE']
    }
    
    df_nuevo = pd.DataFrame(datos)
    
    if not os.path.isfile(archivo):
        df_nuevo.to_csv(archivo, index=False)
    else:
        df_nuevo.to_csv(archivo, mode='a', header=False, index=False)
    print(f"✅ Registro guardado para {ticker}")