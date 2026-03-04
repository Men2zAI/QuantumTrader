import pandas as pd
import yfinance as yf
import json
import os

STOP_LOSS_LIMIT = -2.0 

def actualizar_billetera(ganancia_porcentaje, monto_invertido):
    archivo = 'wallet.json'
    with open(archivo, 'r') as f:
        wallet = json.load(f)
    
    # Calculamos la ganancia basada en el monto específico de esa operación
    cambio_dinero = float(monto_invertido) * (ganancia_porcentaje / 100)
    wallet['saldo_total'] += cambio_dinero
    
    with open(archivo, 'w') as f:
        json.dump(wallet, f, indent=4)
    
    return wallet['saldo_total']

def validar_predicciones():
    archivo = 'historial_decisiones.csv'
    if not os.path.exists(archivo): return
    df = pd.read_csv(archivo)
    
    for index, row in df.iterrows():
        if row['resultado_real'] == 'PENDIENTE':
            # PROTECCIÓN: Si es una operación vieja sin columna 'monto', usamos 100
            monto_op = float(row['monto']) if 'monto' in df.columns else 100.0
            
            if "NEUTRAL" in str(row['prediccion']):
                df.at[index, 'resultado_real'] = "⚪ NO OPERADO"
                continue
            
            ticker, p_entrada, pred = row['ticker'], float(row['precio_entrada']), row['prediccion']
            data = yf.Ticker(ticker).history(period="1d")
            if data.empty: continue
            p_actual = data['Close'].iloc[-1]
            
            diff_porc = ((p_actual - p_entrada) / p_entrada) * 100
            ganancia_real = diff_porc if "COMPRA" in pred else -diff_porc
            
            # Pasamos ambos argumentos a la billetera
            if ganancia_real <= STOP_LOSS_LIMIT:
                saldo = actualizar_billetera(STOP_LOSS_LIMIT, monto_op)
                df.at[index, 'resultado_real'] = f"🛑 STOP LOSS ({STOP_LOSS_LIMIT}% | ${saldo:.2f})"
            else:
                saldo = actualizar_billetera(ganancia_real, monto_op)
                icono = "✅" if ganancia_real > 0 else "❌"
                df.at[index, 'resultado_real'] = f"{icono} ({round(ganancia_real, 2)}% | ${saldo:.2f})"

    df.to_csv(archivo, index=False)