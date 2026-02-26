import yfinance as ticker_data
import pandas as pd

def obtener_datos(symbol):
    """
    Descarga datos históricos para el análisis.
    Usamos 1 mes de datos por hora para tener precisión en los indicadores.
    """
    df = ticker_data.download(symbol, period="1mo", interval="1h", auto_adjust=True)
    return df

def predecir(df, ticker):
    """
    Cerebro de la IA con Triple Confirmación y ajuste por activo.
    """
    # 1. Parámetros Básicos
    ultimo_cierre = df['Close'].iloc[-1].item()
    
    # --- FILTRO DE INGENIERÍA: Ajuste por Activo ---
    # Para MSFT usamos una media de 50 (más lenta/segura) debido a su ruido actual.
    # Para el resto seguimos con 20 para captar tendencias más rápidas.
    periodo_sma = 50 if ticker == "MSFT" else 20
    sma = df['Close'].rolling(window=periodo_sma).mean().iloc[-1].item()
    
    # 2. Sensor de Momento (RSI Manual)
    delta = df['Close'].diff()
    ganancia = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1].item()
    perdida = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1].item()
    rs = ganancia / perdida if perdida != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    
    # 3. Sensor de Fuerza (Volumen)
    vol_hoy = df['Volume'].iloc[-1].item()
    vol_med = df['Volume'].rolling(window=20).mean().iloc[-1].item()

    # --- LÓGICA DE ALTA CONFIANZA ---
    # Una señal de COMPRA solo es válida si:
    # A) Precio está sobre la tendencia (SMA)
    # B) El mercado no está sobrecalentado (RSI < 70)
    # C) Hay interés real de compra (Volumen > Media)
    es_alcista = (ultimo_cierre > sma) and (rsi < 70) and (vol_hoy > vol_med)
    
    # Una señal de VENTA se activa si el precio rompe la tendencia hacia abajo
    es_bajista = (ultimo_cierre < sma) and (rsi > 30)

    # 4. Cálculo de Fiabilidad Dinámica
    # Basada en la distancia porcentual a la media móvil
    distancia = abs(ultimo_cierre - sma) / sma
    fiabilidad = round(min(52.6 + (distancia * 100), 99.0), 2)

    # 5. Veredicto Final
    if es_alcista:
        señal = "🚀 COMPRA (ALTA CONFIANZA)"
    elif es_bajista:
        señal = "📉 VENTA (TENDENCIA BAJISTA)"
    else:
        # Si no se cumplen todos los sensores, el bot protege el capital
        señal = "⚪ NEUTRAL (ESPERANDO CONFIRMACIÓN)"
        
    return señal, round(ultimo_cierre, 2), fiabilidad