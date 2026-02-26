import pandas as pd
import yfinance as yf
import os

def validar_predicciones():
    archivo = 'historial_decisiones.csv'
    if not os.path.exists(archivo):
        return

    df = pd.read_csv(archivo)
    
    # Solo auditamos las que están "PENDIENTE"
    for index, row in df.iterrows():
        if row['resultado_real'] == 'PENDIENTE':
            if "NEUTRAL" in row['prediccion']:
               df.at[index, 'resultado_real'] = "⚪ NO OPERADO"
               continue
            ticker = row['ticker']
            precio_entrada = float(row['precio_entrada'])
            prediccion = row['prediccion']
            
            # Obtener precio actual de mercado
            data = yf.Ticker(ticker).history(period="1d")
            if data.empty: continue
            precio_actual = round(float(data['Close'].iloc[-1]), 2)
            
            # Calcular diferencia
            diferencia_usd = round(precio_actual - precio_entrada, 2)
            porcentaje = round((diferencia_usd / precio_entrada) * 100, 2)
            
            # Lógica de acierto/fallo con margen
            acerto = False
            if "COMPRA" in prediccion and precio_actual > precio_entrada:
                acerto = True
            elif "VENTA" in prediccion and precio_actual < precio_entrada:
                acerto = True
            
            # Formatear el resultado con el "por cuánto"
            icono = "✅" if acerto else "❌"
            resultado = f"{icono} ({porcentaje}% | ${diferencia_usd})"
            
            df.at[index, 'resultado_real'] = resultado
            print(f"Auditor: {ticker} actualizado -> {resultado}")

    df.to_csv(archivo, index=False)

if __name__ == "__main__":
    validar_predicciones()