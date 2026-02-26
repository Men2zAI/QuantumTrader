import yfinance as yf
import pandas as pd

def iniciar_backtest(ticker):
    print(f"⌛ Descargando 1 año de historia para {ticker}...")
    # Descargamos datos diarios del último año
    df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)
    
    if df.empty: 
        print(f"❌ No se pudieron obtener datos para {ticker}")
        return

    aciertos = 0
    total = 0
    
    # Empezamos en el día 20 para tener suficiente historial para la media móvil
    for i in range(20, len(df) - 1):
        # .item() extrae el valor numérico puro de la celda
        precio_entonces = df['Close'].iloc[i].item()
        
        # Calculamos la media móvil del periodo correspondiente
        sma_20 = df['Close'].rolling(window=20).mean().iloc[i].item()
        
        # El resultado real al día siguiente (lo que realmente pasó)
        precio_mañana = df['Close'].iloc[i+1].item()
        
        # Lógica de decisión: 
        # Si precio > media = Predicción de subida (True)
        # Si precio < media = Predicción de bajada (False)
        prediccion_sube = precio_entonces > sma_20
        realidad_subio = precio_mañana > precio_entonces
        
        # Si la predicción coincide con la realidad, es un acierto
        if prediccion_sube == realidad_subio:
            aciertos += 1
        total += 1

    if total > 0:
        precision = round((aciertos / total) * 100, 2)
        print(f"📊 Resultado para {ticker}:")
        print(f"   - Operaciones simuladas: {total}")
        print(f"   - Precisión histórica: {precision}%")
    else:
        print(f"⚠️ No hubo suficientes datos para procesar {ticker}")

if __name__ == "__main__":
    # Lista de empresas para el test
    for t in ["NVDA", "AAPL", "MSFT", "TSLA", "GOOGL"]:
        iniciar_backtest(t)