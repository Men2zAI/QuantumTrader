import pandas as pd
import yfinance as yf
import json
import os

STOP_LOSS_LIMIT = -2.0 # Tu nuevo límite de seguridad

def actualizar_billetera(ganancia_porcentaje):
    with open('wallet.json', 'r') as f:
        wallet = json.load(f)
    
    # Calculamos cuánto ganamos/perdemos sobre la inversión de $100
    cambio_dinero = wallet['inversion_por_operacion'] * (ganancia_porcentaje / 100)
    wallet['saldo_total'] += cambio_dinero
    
    with open('wallet.json', 'w') as f:
        json.dump(wallet, f, indent=4)
    return wallet['saldo_total']

def validar_predicciones():
    archivo = 'historial_decisiones.csv'
    if not os.path.exists(archivo): return
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
            
            diff_porc = ((precio_actual - precio_entrada) / precio_entrada) * 100
            
            # Ajuste de signo según la apuesta (Compra o Venta)
            es_bullish = "COMPRA" in prediccion
            ganancia_porc_real = diff_porc if es_bullish else -diff_porc
            
            # --- Lógica de Dinero ---
            if ganancia_porc_real <= STOP_LOSS_LIMIT:
                final_porc = STOP_LOSS_LIMIT
                nuevo_saldo = actualizar_billetera(final_porc)
                df.at[index, 'resultado_real'] = f"🛑 STOP LOSS ({final_porc}% | ${nuevo_saldo:.2f})"
            else:
                nuevo_saldo = actualizar_billetera(ganancia_porc_real)
                icono = "✅" if ganancia_porc_real > 0 else "❌"
                df.at[index, 'resultado_real'] = f"{icono} ({round(ganancia_porc_real, 2)}% | ${nuevo_saldo:.2f})"

    df.to_csv(archivo, index=False)