import pandas as pd
import yfinance as yf
import json
import os

STOP_LOSS_LIMIT = -2.0  # Fusible de seguridad al 2%

def actualizar_billetera(ganancia_porcentaje):
    archivo = 'wallet.json'
    with open(archivo, 'r') as f:
        wallet = json.load(f)
    
    # Ganancia real sobre los $100 invertidos
    cambio_dinero = wallet['inversion_por_operacion'] * (ganancia_porcentaje / 100)
    wallet['saldo_total'] += cambio_dinero
    
    with open(archivo, 'w') as f:
        json.dump(wallet, f, indent=4)
    
    registrar_balance_diario(wallet['saldo_total'])
    return wallet['saldo_total']

def registrar_balance_diario(saldo_final):
    archivo_hist = 'balance_history.csv'
    fecha = pd.Timestamp.now().strftime('%Y-%m-%d')
    nuevo = pd.DataFrame({'fecha': [fecha], 'saldo': [saldo_final]})
    if os.path.exists(archivo_hist):
        hist = pd.read_csv(archivo_hist)
        hist = pd.concat([hist[hist['fecha'] != fecha], nuevo])
    else:
        hist = nuevo
    hist.to_csv(archivo_hist, index=False)

def validar_predicciones():
    archivo = 'historial_decisiones.csv'
    if not os.path.exists(archivo): return
    df = pd.read_csv(archivo)
    
    for index, row in df.iterrows():
        if row['resultado_real'] == 'PENDIENTE':
            if "NEUTRAL" in str(row['prediccion']):
                df.at[index, 'resultado_real'] = "⚪ NO OPERADO"
                continue
            
            ticker, p_entrada, pred = row['ticker'], float(row['precio_entrada']), row['prediccion']
            data = yf.Ticker(ticker).history(period="1d")
            if data.empty: continue
            p_actual = data['Close'].iloc[-1]
            
            diff_porc = ((p_actual - p_entrada) / p_entrada) * 100
            ganancia_real = diff_porc if "COMPRA" in pred else -diff_porc
            
            if ganancia_real <= STOP_LOSS_LIMIT:
                saldo = actualizar_billetera(STOP_LOSS_LIMIT)
                df.at[index, 'resultado_real'] = f"🛑 STOP LOSS ({STOP_LOSS_LIMIT}% | ${saldo:.2f})"
            else:
                saldo = actualizar_billetera(ganancia_real)
                icono = "✅" if ganancia_real > 0 else "❌"
                df.at[index, 'resultado_real'] = f"{icono} ({round(ganancia_real, 2)}% | ${saldo:.2f})"

    df.to_csv(archivo, index=False)