import pandas as pd
import yfinance as yf
import json
import os
from datetime import datetime

# ⚙️ PARÁMETROS DEL ACTUADOR DINÁMICO
STOP_LOSS_INICIAL = -2.0 
ACTIVACION_TRAILING = 1.5  # Empieza a proteger ganancias después de superar el +1.5%
DISTANCIA_TRAILING = 1.0   # Persigue el precio a un 1.0% de distancia del pico máximo

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
    
    # Inyectamos la columna de memoria si es la primera vez que usamos Trailing Stop
    if 'max_ganancia' not in df.columns:
        df['max_ganancia'] = 0.0
        
    # SENSOR DE TIEMPO: Detecta si es Viernes y es el final de la sesión
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
            
            # --- MOTOR TRAILING STOP DINÁMICO ---
            max_historico = float(row['max_ganancia'])
            
            # 1. Actualizar el récord máximo de ganancias en la memoria
            if ganancia_maxima > max_historico:
                max_historico = ganancia_maxima
                df.at[index, 'max_ganancia'] = max_historico
                
            # 2. Calcular el límite actual (Muro de hierro)
            if max_historico >= ACTIVACION_TRAILING:
                # El stop loss sube para bloquear ganancias (Ej. Si sube a +4%, el stop se pone en +3%)
                stop_dinamico = max_historico - DISTANCIA_TRAILING
            else:
                # El stop loss se queda en su nivel original de defensa (-2.0%)
                stop_dinamico = STOP_LOSS_INICIAL
                
            # --- EVALUACIÓN DE SALIDAS ---
            
            # ¿El precio cayó por debajo de nuestro muro dinámico?
            if ganancia_minima <= stop_dinamico:
                saldo = actualizar_billetera(stop_dinamico, monto_op)
                
                # Reporte inteligente para saber si perdimos o aseguramos ganancias
                if stop_dinamico > 0:
                    df.at[index, 'resultado_real'] = f"🚀 TRAILING STOP (+{round(stop_dinamico, 2)}% | ${saldo:.2f})"
                else:
                    df.at[index, 'resultado_real'] = f"🛑 STOP LOSS ({round(stop_dinamico, 2)}% | ${saldo:.2f})"
            
            # PROTOCOLO DE DEFENSA: Cierre obligatorio de Viernes
            elif es_cierre_semana:
                saldo = actualizar_billetera(ganancia_cierre, monto_op)
                icono = "⏳" if ganancia_cierre > 0 else "🛡️"
                df.at[index, 'resultado_real'] = f"{icono} LIQUIDACIÓN VIERNES ({round(ganancia_cierre, 2)}% | ${saldo:.2f})"
            
            # Paciencia: El precio sigue subiendo y empujando el Trailing Stop hacia arriba
            else:
                pass 

    # Guardamos la memoria actualizada
    df.to_csv(archivo, index=False)