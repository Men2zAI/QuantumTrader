import yfinance as ticker_data
import pandas as pd
import numpy as np

def obtener_datos(symbol):
    df = ticker_data.download(symbol, period="1mo", interval="1h", auto_adjust=True)
    if df.empty:
        raise ValueError(f"No hay datos para {symbol}")
    return df

def predecir(df):
    # 1. Obtener precio y SMA
    ultimo_cierre = float(df['Close'].iloc[-1])
    sma_20 = float(df['Close'].rolling(window=20).mean().iloc[-1])
    
    # 2. Calcular la "Fuerza de la Señal" (Distancia a la media)
    distancia = abs(ultimo_cierre - sma_20) / sma_20
    
    # 3. Calcular fiabilidad dinámica
    # Base de 52.6% (tu precisión base) + un bono por la fuerza de la tendencia
    # Limitamos el máximo a 99% para ser realistas
    fiabilidad_dinamica = 52.6 + (distancia * 100)
    fiabilidad_final = round(min(fiabilidad_dinamica, 99.0), 2)
    
    # 4. Determinar señal
    if ultimo_cierre > sma_20:
        señal = "COMPRA (BULLISH)"
    else:
        señal = "VENTA (BEARISH)"
        
    return señal, round(ultimo_cierre, 2), fiabilidad_final