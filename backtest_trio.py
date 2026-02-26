import yfinance as yf
import pandas as pd
import pandas_ta as ta # Librería técnica potente

def backtest_avanzado(ticker):
    print(f"🔬 Analizando {ticker} con el 'Trio de Sensores'...")
    df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)
    
    if df.empty: return

    # 1. Añadimos los indicadores
    df['SMA_20'] = ta.sma(df['Close'], length=20)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['SMA_Vol'] = ta.sma(df['Volume'], length=20)

    aciertos = 0
    total = 0

    for i in range(20, len(df) - 1):
        precio_hoy = df['Close'].iloc[i].item()
        rsi_hoy = df['RSI'].iloc[i].item()
        vol_hoy = df['Volume'].iloc[i].item()
        vol_med = df['SMA_Vol'].iloc[i].item()
        sma_hoy = df['SMA_20'].iloc[i].item()
        
        precio_mañana = df['Close'].iloc[i+1].item()

        # --- Lógica de IA Robusta ---
        # Compra solo si: tendencia es alcista Y no está sobrecomprado Y hay volumen fuerte
        pred_sube = (precio_hoy > sma_hoy) and (rsi_hoy < 65) and (vol_hoy > vol_med)
        
        # Para el backtest, solo evaluamos los días donde el bot se atrevió a dar una señal
        if pred_sube:
            realidad_subio = precio_mañana > precio_hoy
            if realidad_subio:
                aciertos += 1
            total += 1

    if total > 0:
        print(f"📊 Resultados para {ticker}:")
        print(f"   - Señales de alta confianza emitidas: {total}")
        print(f"   - Precisión real: {round((aciertos/total)*100, 2)}%")
    else:
        print(f"⚠️ El bot no encontró señales con tanta exigencia.")

if __name__ == "__main__":
    for t in ["NVDA", "AAPL", "MSFT", "TSLA"]:
        backtest_avanzado(t)