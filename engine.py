import yfinance as yf
import pandas as pd
import pandas_ta as ta
from scipy.signal import argrelextrema
import numpy as np

def get_market_signals(ticker):
    # 1. Captura de Señal (Sensing)
    df = yf.download(ticker, period="1y", interval="1d")
    
    # 2. Limpieza de Ruido (Filtro EMA)
    # Usamos Media Móvil Exponencial (EMA) que reacciona más rápido que la Simple
    df['EMA_20'] = ta.ema(df['Close'], length=20)
    df['RSI'] = ta.rsi(df['Close'], length=14) # Índice de Fuerza Relativa

    # 3. Detección Matemática de Soportes y Resistencias
    # Buscamos mínimos locales en un rango de 20 días
    n = 20 
    df['Soporte'] = df.iloc[argrelextrema(df.Close.values, np.less_equal, order=n)[0]]['Close']
    df['Resistencia'] = df.iloc[argrelextrema(df.Close.values, np.greater_equal, order=n)[0]]['Close']

    ultimo_precio = df['Close'].iloc[-1].item()
    ultimo_soporte = df['Soporte'].dropna().iloc[-1].item()
    
    # 4. Lógica de Decisión (Smart Computing)
    print(f"\n--- {ticker} Status ---")
    print(f"Precio Actual: {ultimo_precio:.2f}")
    print(f"Soporte más cercano: {ultimo_soporte:.2f}")
    
    # Si el precio está cerca del soporte y el RSI indica que está "barato" (<40)
    if ultimo_precio <= ultimo_soporte * 1.02 and df['RSI'].iloc[-1] < 45:
        return "🚀 SEÑAL: Zona de compra detectada. Precio cerca de soporte con RSI bajo."
    elif ultimo_precio > ultimo_soporte * 1.15:
        return "⚠️ ALERTA: Precio muy alejado del soporte. Riesgo de corrección."
    else:
        return "🔭 ESTADO: Neutral. Esperando retroceso al soporte."

# Ejecución
print(get_market_signals("NVDA"))