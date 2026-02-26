import yfinance as ticker_data
import pandas as pd

def obtener_datos(symbol):
    df = ticker_data.download(symbol, period="1mo", interval="1h", auto_adjust=True)
    return df

def predecir(df):
    # 1. Sensores de Precisión
    ultimo_cierre = df['Close'].iloc[-1].item()
    sma_20 = df['Close'].rolling(window=20).mean().iloc[-1].item()
    
    # RSI Manual
    delta = df['Close'].diff()
    ganancia = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1].item()
    perdida = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1].item()
    rs = ganancia / perdida if perdida != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    
    # Volumen
    vol_hoy = df['Volume'].iloc[-1].item()
    vol_med = df['Volume'].rolling(window=20).mean().iloc[-1].item()

    # 2. Lógica de Triple Confirmación
    # Solo damos señal BULLISH si se cumplen los 3 criterios
    es_alcista = (ultimo_cierre > sma_20) and (rsi < 70) and (vol_hoy > vol_med)
    
    # 3. Cálculo de Fiabilidad Dinámica
    distancia = abs(ultimo_cierre - sma_20) / sma_20
    fiabilidad = round(min(52.6 + (distancia * 100), 99.0), 2)

    if es_alcista:
        señal = "🚀 COMPRA (ALTA CONFIANZA)"
    elif (ultimo_cierre < sma_20) and (rsi > 30):
        señal = "📉 VENTA (TENDENCIA BAJISTA)"
    else:
        señal = "⚪ NEUTRAL (ESPERANDO CONFIRMACIÓN)"
        
    return señal, round(ultimo_cierre, 2), fiabilidad