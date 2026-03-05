import pandas as pd
import os

def guardar_registro(ticker, precio, prediccion, fiabilidad, monto):
    archivo = 'historial_decisiones.csv'
    fecha = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')
    
    nuevo_dato = pd.DataFrame({
        'fecha': [fecha],
        'ticker': [ticker],
        'precio_entrada': [precio],
        'prediccion': [prediccion],
        'fiabilidad': [fiabilidad],
        'monto': [monto], # <-- Columna nueva para rastrear la inversión dinámica
        'resultado_real': ['PENDIENTE']
    })
    
    if os.path.exists(archivo):
        df = pd.read_csv(archivo)
        df = pd.concat([df, nuevo_dato], ignore_index=True)
    else:
        df = nuevo_dato
        
    df.to_csv(archivo, index=False)