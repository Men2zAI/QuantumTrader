import pandas as pd
import os
from datetime import datetime

LOG_FILE = "wallstreet_ledger.csv"

def guardar_registro(ticker, precio, señal, fiabilidad, monto):
    """
    Escribe cada decisión táctica del Nodo Alpha en un archivo de auditoría.
    """
    try:
        # Si el archivo no existe, creamos la estructura base
        if not os.path.exists(LOG_FILE):
            df_base = pd.DataFrame(columns=[
                'timestamp', 'ticker', 'precio_ejecucion', 
                'señal', 'fiabilidad_ia', 'monto_invertido'
            ])
            df_base.to_csv(LOG_FILE, index=False)

        # Leemos el historial, añadimos la nueva operación y guardamos
        df = pd.read_csv(LOG_FILE)
        nuevo_registro = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ticker': ticker,
            'precio_ejecucion': round(precio, 2),
            'señal': señal,
            'fiabilidad_ia': fiabilidad,
            'monto_invertido': round(monto, 2)
        }
        
        df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
        df.to_csv(LOG_FILE, index=False)
        print(f"📝 Registro contable guardado: {ticker} (Confianza: {fiabilidad}%)")
        
    except Exception as e:
        print(f"⚠️ Error de escritura en el ledger de Wall Street: {e}")

if __name__ == "__main__":
    # Prueba rápida de diagnóstico local
    print("Iniciando prueba de escritura...")
    guardar_registro("AAPL", 175.50, "COMPRA CUÁDRUPLE", 82.5, 1500.00)
    print("Verifica si se creó el archivo 'wallstreet_ledger.csv'.")