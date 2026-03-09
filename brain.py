import yfinance as yf
import pandas as pd
import numpy as np
import joblib
import os
import warnings

# Mantenemos la terminal limpia para el reporte final
warnings.filterwarnings('ignore')

def crear_features_produccion(df, tipo="ticker"):
    """
    Motor de Inferencia: Calcula la red de sensores EXACTAMENTE igual que 
    el entrenamiento, pero SIN intentar predecir el Target futuro.
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

        # Solo enviamos las variables matemáticas, sin el 'Target'
        features_ticker = ['Retorno', 'RSI', 'MACD_Hist', 'Distancia_BB_Inf', 'ATR', 'SMA_20', 'SMA_50']
        return df[features_ticker]

def escanear_mercado_en_vivo(ticker, umbral_confianza=0.65):
    ruta_modelo = f"modelos/modelo_{ticker}.pkl"
    if not os.path.exists(ruta_modelo):
        print(f"❌ ERROR: Cerebro no encontrado para {ticker}. Entrénalo primero.")
        return

    # 1. DESPERTAR A LA IA
    modelo = joblib.load(ruta_modelo)
    
    # 2. DESCARGAR SENSORES (Solo 100 días para ultra velocidad)
    df_ticker = yf.Ticker(ticker).history(period="100d", interval="1d")
    df_qqq = yf.Ticker("QQQ").history(period="100d", interval="1d")
    df_vix = yf.Ticker("^VIX").history(period="100d", interval="1d")
    
    if df_ticker.empty or df_qqq.empty or df_vix.empty:
        return
    
    # Sincronización de relojes para cruzar datos sin error
    df_ticker.index = pd.to_datetime(df_ticker.index).tz_localize(None).normalize()
    df_qqq.index = pd.to_datetime(df_qqq.index).tz_localize(None).normalize()
    df_vix.index = pd.to_datetime(df_vix.index).tz_localize(None).normalize()
    
    feat_ticker = crear_features_produccion(df_ticker, tipo="ticker")
    feat_qqq = crear_features_produccion(df_qqq, tipo="qqq")
    feat_vix = crear_features_produccion(df_vix, tipo="vix")
    
    df_unido = feat_ticker.join(feat_qqq, how='inner').join(feat_vix, how='inner').dropna()
    df_unido = df_unido.sort_index()
    
    if df_unido.empty:
        return
        
    # 3. EXTRAER LA "FOTO" DEL MILISEGUNDO ACTUAL
    datos_hoy = df_unido.iloc[-1:]
    
    # 4. EL ORÁCULO TOMA LA DECISIÓN
    probabilidad = modelo.predict_proba(datos_hoy)[0][1]
    
    # 5. GESTIÓN DE RIESGO INTELIGENTE
    precio_actual = df_ticker['Close'].iloc[-1]
    atr_actual = datos_hoy['ATR'].iloc[-1]
    
    # Tu estrategia exacta: Take Profit Dinámico (1.5x ATR) y Stop Loss Estricto (-2%)
    take_profit_usd = precio_actual + (atr_actual * 1.5)
    stop_loss_usd = precio_actual - (precio_actual * 0.02) 
    
    print("-" * 50)
    print(f"🔬 ÉLITE EXPLORACIÓN: {ticker}")
    print(f"📍 Precio Actual: ${precio_actual:.2f}")
    print(f"📊 Confianza de la IA: {probabilidad * 100:.2f}%")
    
    if probabilidad >= umbral_confianza:
        print(f"✅ ¡SEÑAL DE COMPRA DISPARADA!")
        print(f"🎯 Take Profit: ${take_profit_usd:.2f} | 🛡️ Stop Loss: ${stop_loss_usd:.2f}")
        # Aquí es donde en el futuro conectarás el código para tu Broker.
    else:
        print(f"⏳ Señal descartada (Requiere {umbral_confianza*100}%)")

if __name__ == "__main__":
    print("🚀 INICIANDO PROTOCOLO DE CONEXIÓN CEREBRAL...")
    mi_cartera = ["MSFT", "PYPL", "NVDA"]
    
    for empresa in mi_cartera:
        # Ejecutamos el escáner exigiendo nuestro muro del 65% a NVIDIA y Microsoft.
        escanear_mercado_en_vivo(empresa, umbral_confianza=0.65)
    print("-" * 50)