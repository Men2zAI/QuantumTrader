import pandas as pd
import joblib
import time
import requests
import os
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
import crypto_brain
import crypto_xgboost

# 1. Cargar llaves y configuración de red
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MODELO_FILE = "modelo_cripto_BTCUSDT.pkl"

def enviar_telegram(mensaje):
    """Transmite la señal a través del bot de Telegram"""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("⚠️ Credenciales de Telegram no detectadas en entorno.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"⚠️ Error en transmisión de red: {e}")

try:
    cerebro = joblib.load(MODELO_FILE)
    print("🧠 [NODO BETA CLOUD] Cerebro cuántico cargado.")
except FileNotFoundError:
    print("⚠️ Error: No se encontró el cerebro entrenado (.pkl).")
    exit()

def calcular_atr(df, periodos=14):
    """Calcula la volatilidad pura para definir objetivos de salida"""
    high_low = df['high'] - df['low']
    high_close = abs(df['high'] - df['close'].shift())
    low_close = abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(periodos).mean().iloc[-1]

def ejecutar_escaneo_tiempo_real(simbolo='BTC/USDT'):
    print(f"\n📡 [{datetime.now().strftime('%H:%M:%S')}] Iniciando intercepción CCXT para {simbolo}...")
    
    df_reciente = crypto_brain.obtener_historico_cripto(simbolo, '1h', 50)
    if df_reciente.empty:
        return
        
    df_procesado = crypto_xgboost.calcular_indicadores_flash(df_reciente.copy())
    ultima_fila = df_procesado.iloc[-1:]
    
    features = ['open', 'high', 'low', 'close', 'volume', 'variacion_pct', 
                'RSI', 'SMA_20', 'Band_Upper', 'Band_Lower', 
                'MACD', 'MACD_Signal', 'MACD_Hist', 'Vol_ROC',
                'Lag_1_Close', 'Lag_2_Close', 'Lag_1_Vol']
                
    X_presente = ultima_fila[features]
    
    precio_actual = ultima_fila['close'].values[0]
    rsi_actual = ultima_fila['RSI'].values[0]
    macd_hist = ultima_fila['MACD_Hist'].values[0]
    
    # 🎯 Inferencia de IA
    prediccion = cerebro.predict(X_presente)[0]
    probabilidad = cerebro.predict_proba(X_presente)[0]
    prob_subir = probabilidad[1] * 100
    
    atr = calcular_atr(df_reciente)
    take_profit = precio_actual + (atr * 1.5)
    stop_loss = precio_actual - (atr * 1.0)
    
    if prediccion == 1 and prob_subir > 53.0:
        estado = "🟢 COMPRA TÁCTICA"
        accion = (f"🎯 *Take Profit:* ${take_profit:,.2f}\n"
                  f"🛡️ *Stop Loss:* ${stop_loss:,.2f}")
    elif prediccion == 0:
        estado = "🔴 PELIGRO DE CAÍDA (Short/Espera)"
        accion = "La IA detecta distribución. Mantener liquidez."
    else:
        estado = "🟡 INCERTIDUMBRE (Neutral)"
        accion = "Señal débil. Esperar mejor estructura de red."

    mensaje_tg = (f"🤖 *NODO BETA CRIPTO* ({simbolo})\n"
                  f"⏱️ {datetime.now().strftime('%H:%M:%S')} UTC\n"
                  f"💰 *Precio:* ${precio_actual:,.2f}\n\n"
                  f"🧠 *Señal:* {estado}\n"
                  f"📈 *Prob. Subida:* {prob_subir:.2f}%\n"
                  f"⚡ *RSI:* {rsi_actual:.1f} | *MACD:* {macd_hist:.1f}\n\n"
                  f"{accion}")
                  
    print(mensaje_tg.replace('*', '')) 
    enviar_telegram(mensaje_tg)

if __name__ == "__main__":
    print("🌐 [CLOUD DAEMON] Ejecución única iniciada. Calculando vectores...")
    ejecutar_escaneo_tiempo_real('BTC/USDT')
    print("🛑 [CLOUD DAEMON] Telemetría enviada. Apagando instancia.")