import yfinance as ticker_data
import pandas as pd

def obtener_datos(symbol):
    """
    Descarga los datos históricos del símbolo especificado.
    """
    # Descargamos el último mes de datos con intervalos de 1 hora
    df = ticker_data.download(symbol, period="1mo", interval="1h")
    if df.empty:
        raise ValueError(f"No se encontraron datos para {symbol}")
    return df

def predecir(df):
    """
    Lógica de IA para decidir si comprar o vender.
    Mantiene la lógica de precisión direccional.
    """
    # Obtenemos el precio actual (último cierre)
    # Usamos .iloc[-1] para evitar errores de formato en versiones nuevas de pandas
    precio_actual = round(float(df['Close'].iloc[-1]), 2)
    
    # --- Simulación de lógica de IA (Aquí iría tu modelo entrenado) ---
    # Por ahora usamos una lógica basada en medias móviles simple
    sma_20 = df['Close'].rolling(window=20).mean().iloc[-1]
    
    fiabilidad = 52.6 # Tu métrica de precisión actual
    
    if precio_actual > sma_20:
        señal = "COMPRA (BULLISH)"
    else:
        señal = "VENTA (BEARISH)"
        
    return señal, precio_actual, fiabilidad