import yfinance as yf
import pandas as pd

def analizar_activo(ticker):
    # 1. Captura de datos (Sensing)
    data = yf.download(ticker, period="60d", interval="1d")
    
    # 2. Procesamiento de señal (Filtrado de ruido)
    # Calculamos la media de 20 días (tendencia corta)
    data['MA20'] = data['Close'].rolling(window=20).mean()
    
    ultimo_precio = data['Close'].iloc[-1]
    media_20 = data['MA20'].iloc[-1]
    
    print(f"\n--- Análisis de {ticker} ---")
    print(f"Precio actual: {ultimo_precio:.2f}")
    
    # 3. Lógica de decisión (Algoritmo básico)
    if ultimo_precio > media_20:
        distancia = ((ultimo_precio - media_20) / media_20) * 100
        return f"TENDENCIA ALCISTA: El precio está {distancia:.2f}% por encima de su media. (ZONA DE FUERZA)"
    else:
        return "TENDENCIA BAJISTA: El precio está por debajo de su media. (PRECAUCIÓN)"

# Prueba con activos que mencionan en el curso
activos = ["NVDA", "AAPL", "QQQ"]
for a in activos:
    resultado = analizar_activo(a)
    print(resultado)