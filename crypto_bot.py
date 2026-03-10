import pandas as pd
import joblib
import os
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
import crypto_brain
import crypto_xgboost
import requests

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MODELO_FILE = "modelo_cripto_BTCUSDT.pkl"
LOG_FINANCIERO = "crypto_balance.csv"

def registrar_operacion_virtual(precio, señal):
    """Fase B: Simulador de Papel Interno"""
    try:
        df_bal = pd.read_csv(LOG_FINANCIERO)
        nuevo_registro = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'balance_usdt': df_bal.iloc[-1]['balance_usdt'], # Por ahora estático
            'activo': 'BTC',
            'operacion': señal,
            'precio_ejecucion': precio
        }
        df_bal = pd.concat([df_bal, pd.DataFrame([nuevo_registro])], ignore_index=True)
        df_bal.to_csv(LOG_FINANCIERO, index=False)
        return "📊 Registro contable actualizado."
    except:
        return "⚠️ Error actualizando balance virtual."

# ... (Mismas funciones enviar_telegram y calcular_atr que ya tienes) ...
def enviar_telegram(mensaje):
    if not TELEGRAM_TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"})
    except: pass

try:
    cerebro = joblib.load(MODELO_FILE)
except:
    exit()

def calcular_atr(df, periodos=14):
    high_low = df['high'] - df['low']
    high_close = abs(df['high'] - df['close'].shift())
    low_close = abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(periodos).mean().iloc[-1]

def ejecutar_escaneo_tiempo_real(simbolo='BTC/USDT'):
    df_reciente = crypto_brain.obtener_historico_cripto(simbolo, '1h', 50)
    if df_reciente.empty: return
        
    df_procesado = crypto_xgboost.calcular_indicadores_flash(df_reciente.copy())
    ultima_fila = df_procesado.iloc[-1:]
    
    features = ['open', 'high', 'low', 'close', 'volume', 'variacion_pct', 
                'RSI', 'SMA_20', 'Band_Upper', 'Band_Lower', 
                'MACD', 'MACD_Signal', 'MACD_Hist', 'Vol_ROC',
                'Lag_1_Close', 'Lag_2_Close', 'Lag_1_Vol']
                
    X_presente = ultima_fila[features]
    precio_actual = ultima_fila['close'].values[0]
    
    prediccion = cerebro.predict(X_presente)[0]
    prob_subir = cerebro.predict_proba(X_presente)[0][1] * 100
    
    atr = calcular_atr(df_reciente)
    tp, sl = precio_actual + (atr * 1.5), precio_actual - (atr * 1.0)
    
    log_msg = ""
    if prediccion == 1 and prob_subir > 53.0:
        estado = "🟢 COMPRA TÁCTICA"
        log_msg = registrar_operacion_virtual(precio_actual, "BUY")
    elif prediccion == 0:
        estado = "🔴 PELIGRO DE CAÍDA"
        log_msg = registrar_operacion_virtual(precio_actual, "SELL_OR_WAIT")
    else:
        estado = "🟡 NEUTRAL"

    mensaje_tg = (f"🤖 *NODO BETA* (Vía KuCoin)\n"
                  f"💰 *BTC:* ${precio_actual:,.2f}\n"
                  f"🧠 *Señal:* {estado} ({prob_subir:.1f}%)\n"
                  f"🎯 *TP:* ${tp:,.2f} | *SL:* ${sl:,.2f}\n"
                  f"{log_msg}")
                  
    enviar_telegram(mensaje_tg)

if __name__ == "__main__":
    ejecutar_escaneo_tiempo_real('BTC/USDT')