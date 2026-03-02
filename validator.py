import pandas as pd
import yfinance as yf

# CONFIGURACIÓN DE SEGURIDAD REFORZADA
STOP_LOSS_LIMIT = -2.0  # Bajamos del 5% al 2% para proteger el capital

def validar_predicciones():
    archivo = 'historial_decisiones.csv'
    if not pd.io.common.file_exists(archivo): return
    df = pd.read_csv(archivo)
    
    for index, row in df.iterrows():
        if row['resultado_real'] == 'PENDIENTE':
            if "NEUTRAL" in str(row['prediccion']):
                df.at[index, 'resultado_real'] = "⚪ NO OPERADO"
                continue
            
            ticker = row['ticker']
            precio_entrada = float(row['precio_entrada'])
            prediccion = row['prediccion']
            
            data = yf.Ticker(ticker).history(period="1d")
            if data.empty: continue
            precio_actual = data['Close'].iloc[-1]
            
            diff_usd = precio_actual - precio_entrada
            diff_porc = (diff_usd / precio_entrada) * 100
            
            # Lógica de Fusible (Ahora al 2%)
            variacion_en_contra = -diff_porc if "COMPRA" in prediccion else diff_porc
            
            if variacion_en_contra < STOP_LOSS_LIMIT:
                pérdida_limitada_usd = precio_entrada * (STOP_LOSS_LIMIT / 100)
                # El signo depende de la dirección de la apuesta
                pérdida_final = -abs(pérdida_limitada_usd) if "COMPRA" in prediccion else abs(pérdida_limitada_usd)
                df.at[index, 'resultado_real'] = f"🛑 STOP LOSS ({STOP_LOSS_LIMIT}% | ${round(pérdida_final, 2)})"
            else:
                es_bullish = "COMPRA" in prediccion
                exito = (es_bullish and diff_usd > 0) or (not es_bullish and diff_usd < 0)
                icono = "✅" if exito else "❌"
                df.at[index, 'resultado_real'] = f"{icono} ({round(diff_porc, 2)}% | ${round(diff_usd, 2)})"

    df.to_csv(archivo, index=False)