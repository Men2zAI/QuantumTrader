import yfinance as yf
import pandas as pd
import numpy as np
import joblib
import os
import warnings

warnings.filterwarnings('ignore')

def crear_features_produccion(df, tipo="ticker"):
    """
    Motor de Extracción V7: Transforma los datos crudos en la matriz de sensores
    exacta que el modelo XGBoost Bayesiano (con Volumen) espera recibir.
    """
    df['Retorno'] = df['Close'].pct_change()
    
    if tipo == "qqq":
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['QQQ_Tendencia'] = np.where(df['Close'] > df['SMA_50'], 1, -1)
        df['QQQ_Retorno'] = df['Retorno']
        return df[['QQQ_Tendencia', 'QQQ_Retorno']]
        
    elif tipo == "vix":
        df['VIX_Nivel'] = df['Close']
        df['VIX_Retorno'] = df['Retorno']
        return df[['VIX_Nivel', 'VIX_Retorno']]
        
    else:
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        delta = df['Close'].diff()
        ganancia = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        perdida = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = ganancia / perdida
        df['RSI'] = 100 - (100 / (1 + rs))
        
        df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        df['BB_std'] = df['Close'].rolling(window=20).std()
        df['BB_Lower'] = df['SMA_20'] - (df['BB_std'] * 2)
        df['Distancia_BB_Inf'] = (df['Close'] - df['BB_Lower']) / df['Close']
        
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        df['ATR'] = ranges.max(axis=1).rolling(14).mean()

        # 🌊 INYECCIÓN DE SENSORES VOLUMÉTRICOS PARA PRODUCCIÓN 🌊
        # 1. OBV (On-Balance Volume)
        df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
        
        # 2. VWAP Móvil
        precio_tipico = (df['High'] + df['Low'] + df['Close']) / 3
        df['VWAP_14'] = (precio_tipico * df['Volume']).rolling(window=14).sum() / df['Volume'].rolling(window=14).sum()
        df['Distancia_VWAP'] = (df['Close'] - df['VWAP_14']) / df['VWAP_14']

        # Retenemos 'Close' temporalmente para que el orquestador pueda leer el precio
        # NOTA IMPORTANTE: El orden debe coincidir con el entrenamiento.
        features_ticker = ['Close', 'Retorno', 'RSI', 'MACD_Hist', 'Distancia_BB_Inf', 'ATR', 'SMA_20', 'SMA_50', 'OBV', 'Distancia_VWAP']
        return df[features_ticker]

def obtener_datos(ticker):
    """
    Multiplexor: Descarga y sincroniza la red de sensores (Micro + Macro + Miedo + Volumen)
    para alimentar al orquestador principal.
    """
    try:
        # Aumentamos a 150d porque el OBV necesita un poco más de historial para ser preciso
        df_ticker = yf.Ticker(ticker).history(period="150d", interval="1d")
        df_qqq = yf.Ticker("QQQ").history(period="150d", interval="1d")
        df_vix = yf.Ticker("^VIX").history(period="150d", interval="1d")
        
        if df_ticker.empty or df_qqq.empty or df_vix.empty:
            return None
            
        # Sincronización estricta de relojes
        df_ticker.index = pd.to_datetime(df_ticker.index).tz_localize(None).normalize()
        df_qqq.index = pd.to_datetime(df_qqq.index).tz_localize(None).normalize()
        df_vix.index = pd.to_datetime(df_vix.index).tz_localize(None).normalize()
        
        feat_ticker = crear_features_produccion(df_ticker, tipo="ticker")
        feat_qqq = crear_features_produccion(df_qqq, tipo="qqq")
        feat_vix = crear_features_produccion(df_vix, tipo="vix")
        
        df_unido = feat_ticker.join(feat_qqq, how='inner').join(feat_vix, how='inner').dropna()
        df_unido = df_unido.sort_index()
        
        return df_unido if not df_unido.empty else None
    except Exception as e:
        print(f"⚠️ Error sincronizando sensores para {ticker}: {e}")
        return None

def predecir(df, ticker):
    """
    Procesador Digital: Carga el archivo .pkl, ejecuta la inferencia y 
    devuelve la estructura exacta que el orquestador espera (señal, precio, fiabilidad).
    """
    if df is None or df.empty:
        return "ERROR DE RED", 0.0, 0.0
        
    ruta_modelo = f"modelos/modelo_{ticker}.pkl"
    if not os.path.exists(ruta_modelo):
        return "CEREBRO NO ENTRENADO", 0.0, 0.0
        
    try:
        modelo = joblib.load(ruta_modelo)
        datos_hoy = df.iloc[-1:]
        
        precio_actual = datos_hoy['Close'].iloc[0]
        
        X = datos_hoy.drop(columns=['Close'])
        
        probabilidad = modelo.predict_proba(X)[0][1]
        fiabilidad = probabilidad * 100
        
        if fiabilidad >= 60.0:
            señal = "COMPRA ESTRICTA - ALTA CONFIANZA"
        else:
            señal = "RUIDO DESCARTADO"
            
        return señal, precio_actual, round(fiabilidad, 2)
        
    except Exception as e:
        print(f"⚠️ Error en inferencia para {ticker}: {e}")
        return "ERROR DE PROCESAMIENTO", 0.0, 0.0