import pandas as pd
import yfinance as yf
import json
import os
from datetime import datetime

STOP_LOSS_LIMIT = -2.0 
TAKE_PROFIT_LIMIT = 4.0

def actualizar_billetera(ganancia_porcentaje, monto_invertido):
    archivo = 'wallet.json'
    with open(archivo, 'r') as f:
        wallet = json.load(f)
    
    cambio_dinero = float(monto_invertido) * (ganancia_porcentaje / 100)
    wallet['saldo_total'] += cambio_dinero
    
    with open(archivo, 'w') as f:
        json.dump(wallet, f, indent=4)
    
    return wallet['saldo_total']

def validar_predicciones():
    archivo = 'historial_decisiones.csv'
    if not os.path.exists(archivo): return
    df = pd.read_csv(archivo)
    
    # SENSOR DE TIEMPO: Detecta si es Viernes (4) y es el final de la sesión en Wall Street (>20:00 UTC)
    hora_actual_utc = datetime.utcnow()
    es_cierre_semana = hora_actual_utc.weekday() == 4 and hora_actual_utc.hour >= 20
    
    for index, row in df.iterrows():
        if row['resultado_real'] == 'PENDIENTE':
            monto_op = float(row['monto']) if 'monto' in df.columns else 100.0
            
            if "NEUTRAL" in str(row['prediccion']):
                df.at[index, 'resultado_real'] = "⚪ NO OPERADO"
                continue
            
            ticker, p_entrada, pred = row['ticker'], float(row['precio_entrada']), row['prediccion']
            data = yf.Ticker(ticker).history(period="1d")
            if data.empty: continue
            
            p_actual = data['Close'].iloc[-1]
            p_max = data['High'].iloc[-1]
            p_min = data['Low'].iloc[-1]
            
            if "COMPRA" in pred:
                ganancia_maxima = ((p_max - p_entrada) / p_entrada) * 100
                ganancia_minima = ((p_min - p_entrada) / p_entrada) * 100
                ganancia_cierre = ((p_actual - p_entrada) / p_entrada) * 100
            else: 
                ganancia_maxima = ((p_entrada - p_min) / p_entrada) * 100
                ganancia_minima = ((p_entrada - p_max) / p_entrada) * 100
                ganancia_cierre = ((p_entrada - p_actual) / p_entrada) * 100
            
            # 1. ¿Tocó el Stop Loss?
            if ganancia_minima <= STOP_LOSS_LIMIT:
                saldo = actualizar_billetera(STOP_LOSS_LIMIT, monto_op)
                df.at[index, 'resultado_real'] = f"🛑 STOP LOSS ({STOP_LOSS_LIMIT}% | ${saldo:.2f})"
            
            # 2. ¿Alcanzó el Take Profit?
            elif ganancia_maxima >= TAKE_PROFIT_LIMIT:
                saldo = actualizar_billetera(TAKE_PROFIT_LIMIT, monto_op)
                df.at[index, 'resultado_real'] = f"🎯 TAKE PROFIT ({TAKE_PROFIT_LIMIT}% | ${saldo:.2f})"
            
            # 3. PROTOCOLO DE DEFENSA: Cierre obligatorio de Viernes
            elif es_cierre_semana:
                saldo = actualizar_billetera(ganancia_cierre, monto_op)
                icono = "⏳" if ganancia_cierre > 0 else "🛡️"
                df.at[index, 'resultado_real'] = f"{icono} LIQUIDACIÓN VIERNES ({round(ganancia_cierre, 2)}% | ${saldo:.2f})"
            
            # 4. Paciencia: Sigue PENDIENTE de Lunes a Jueves (o viernes temprano)
            else:
                pass 

    df.to_csv(archivo, index=False)