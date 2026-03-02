import pandas as pd
import re
import json
import os

def actualizar_activos_rentables():
    archivo_csv = 'historial_decisiones.csv'
    archivo_json = 'elegidos.json'
    
    if not os.path.exists(archivo_csv):
        print("⚠️ No hay historial para analizar todavía.")
        return []

    df = pd.read_csv(archivo_csv)
    
    # Filtramos solo lo que ya tiene un resultado final
    df = df[df['resultado_real'].str.contains('✅|❌|🛑', na=False)].copy()
    
    if df.empty:
        print("⚠️ El historial no tiene operaciones cerradas aún.")
        return []

    def extraer_ganancia_neta(row):
        texto = str(row['resultado_real'])
        # Buscamos el valor después del símbolo $
        match = re.search(r'\$\s?(-?\d+\.?\d*)', texto)
        if not match: return 0.0
        
        valor_usd = float(match.group(1))
        
        # Lógica de signo: En el CSV guardamos (Precio_Actual - Precio_Entrada)
        # Si fue VENTA, una diferencia negativa en el precio es GANANCIA positiva
        if "VENTA" in str(row['prediccion']):
            return -valor_usd
        return valor_usd

    df['ganancia_neta'] = df.apply(extraer_ganancia_neta, axis=1)
    
    # Agrupamos por empresa y sumamos todo su histórico
    ranking = df.groupby('ticker')['ganancia_neta'].sum()
    
    # CRITERIO: Solo permitimos operar a los que NO tengan balance negativo
    # NVDA con +$10.27 entra, COST con -$24.08 se queda fuera
    elegidos = ranking[ranking >= 0].index.tolist()
    
    with open(archivo_json, 'w') as f:
        json.dump(elegidos, f)
    
    print(f"✅ Lista de Elegidos actualizada: {elegidos}")
    return elegidos

if __name__ == "__main__":
    actualizar_activos_rentables()