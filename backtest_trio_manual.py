import yfinance as yf
import pandas as pd
import numpy as np

def calcular_rsi(serie, periodo=14):
    delta = serie.diff()
    ganancia = (delta.where(delta > 0, 0)).rolling(window=periodo).mean()
    perdida = (-delta.where(delta < 0, 0)).rolling(window=periodo).mean()
    rs = ganancia / perdida
    return 100 - (100 / (1 + rs))

def backtest_avanzado(ticker):
    print(f"🔬 Analizando {ticker} con lógica de Triple Confirmación...")
    df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)
    
    if df.empty: return

    # 1. Creamos nuestros propios sensores
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_Vol'] = df['Volume'].rolling(window=20).mean()
    df['RSI'] = calcular_rsi(df['Close'])

    aciertos = 0
    total = 0

    # Empezamos en el día 20 para que los promedios estén listos
    for i in range(20, len(df) - 1):
        precio_hoy = df['Close'].iloc[i].item()
        rsi_hoy = df['RSI'].iloc[i].item()
        vol_hoy = df['Volume'].iloc[i].item()
        vol_med = df['SMA_Vol'].iloc[i].item()
        sma_hoy = df['SMA_20'].iloc[i].item()
        
        precio_mañana = df['Close'].iloc[i+1].item()

        # --- Lógica de IA Multivariable ---
        # CONDICIÓN: Tendencia alcista (Precio > SMA) 
        #           Y No agotamiento (RSI < 70) 
        #           Y Fuerza real (Volumen > Media)
        pred_sube = (precio_hoy > sma_hoy) and (rsi_hoy < 70) and (vol_hoy > vol_med)
        
        if pred_sube:
            realidad_subio = precio_mañana > precio_hoy
            if realidad_subio:
                aciertos += 1
            total += 1

    if total > 0:
        precision = round((aciertos / total) * 100, 2)
        print(f"📊 Resultados para {ticker}:")
        print(f"   - Señales filtradas emitidas: {total}")
        print(f"   - Precisión real: {precision}%")
        return precision
    else:
        print(f"⚠️ El filtro es tan estricto que no encontró señales para {ticker}.")
        return 0

if __name__ == "__main__":
    for t in ["NVDA", "AAPL", "MSFT", "TSLA", "GOOGL"]:
        backtest_avanzado(t)