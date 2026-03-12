import pandas as pd
import yfinance as yf
import xgboost as xgb
import numpy as np
import requests # <-- NUEVO MÓDULO DE CAMUFLAJE

def obtener_datos(ticker):
    try:
        # --- INYECCIÓN DE CAMUFLAJE DE RED ---
        sesion_camuflada = requests.Session()
        sesion_camuflada.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        })
        
        # Pasamos la sesión al descargador
        df = yf.download(ticker, period="150d", progress=False, session=sesion_camuflada)
        
        if df.empty:
            raise ValueError(f"No hay datos para {ticker}")
            
        df = df.dropna()
        df['Retorno'] = df['Close'].pct_change()
        df['Volatilidad'] = df['Close'].rolling(window=14).std()
        df['Media_Movil'] = df['Close'].rolling(window=14).mean()
        df['Target'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
        df = df.dropna()
        
        return df
    except Exception as e:
        print(f"⚠️ Error al obtener datos de {ticker}: {e}")
        return pd.DataFrame()

def predecir(df, ticker):
    if df.empty or len(df) < 50:
        return 0, 0, 0
        
    features = ['Retorno', 'Volatilidad', 'Media_Movil']
    X = df[features]
    y = df['Target']
    
    modelo = xgb.XGBClassifier(
        objective='binary:logistic',
        eval_metric='logloss',
        use_label_encoder=False,
        max_depth=3,
        learning_rate=0.05,
        n_estimators=100
    )
    
    # Entrenar con todos los datos menos el último
    modelo.fit(X.iloc[:-1], y.iloc[:-1])
    
    # Predecir el último
    ultimo_dato = X.iloc[[-1]]
    probabilidad = modelo.predict_proba(ultimo_dato)[0][1] * 100
    prediccion = int(modelo.predict(ultimo_dato)[0])
    precio_actual = df['Close'].iloc[-1]
    
    return prediccion, precio_actual, probabilidad