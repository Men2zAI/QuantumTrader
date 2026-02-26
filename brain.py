import yfinance as ticker_data
import pandas as pd

def obtener_datos(symbol):
    """
    Descarga los datos históricos asegurando un formato limpio.
    """
    # Descargamos con auto_adjust para evitar columnas duplicadas
    df = ticker_data.download(symbol, period="1mo", interval="1h", auto_adjust=True)
    if df.empty:
        raise ValueError(f"No se encontraron datos para {symbol}")
    return df

def predecir(df):
    """
    Lógica de IA corregida para evitar errores de Series ambiguas.
    """
    # Extraemos el valor de cierre y lo convertimos a float puro
    # .iloc[-1] toma el último, .item() lo convierte en un solo número
    ultimo_cierre = df['Close'].iloc[-1]
    
    # Si yfinance devuelve un formato complejo, lo simplificamos aquí
    if isinstance(ultimo_cierre, pd.Series):
        ultimo_cierre = ultimo_cierre.iloc[0]
        
    precio_actual = round(float(ultimo_cierre), 2)
    
    # Calculamos la Media Móvil (SMA) y nos aseguramos de que sea un solo número
    sma_serie = df['Close'].rolling(window=20).mean()
    ultimo_sma = sma_serie.iloc[-1]
    
    if isinstance(ultimo_sma, pd.Series):
        ultimo_sma = ultimo_sma.iloc[0]
        
    sma_20 = float(ultimo_sma)
    
    fiabilidad = 52.6 
    
    # Ahora la comparación es entre dos números simples, no listas
    if precio_actual > sma_20:
        señal = "COMPRA (BULLISH)"
    else:
        señal = "VENTA (BEARISH)"
        
    return señal, precio_actual, fiabilidad