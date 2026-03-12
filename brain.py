import os
import pandas as pd
import numpy as np
import xgboost as xgb
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
alpaca = tradeapi.REST(
    os.getenv('ALPACA_API_KEY'), 
    os.getenv('ALPACA_SECRET_KEY'), 
    'https://paper-api.alpaca.markets', 
    api_version='v2'
)

def obtener_datos(ticker):
    try:
        fin = datetime.now() - timedelta(minutes=16) # Evitamos el muro de pago de los últimos 15 min
        inicio = fin - timedelta(days=220) 
        
        # Usamos feed="iex" para el plan gratuito
        barras = alpaca.get_bars(
            ticker, 
            tradeapi.rest.TimeFrame.Day, 
            start=inicio.strftime('%Y-%m-%d'), 
            end=fin.strftime('%Y-%m-%d'),
            feed='iex'
        ).df
        
        if barras.empty:
            raise ValueError(f"Sin datos en Alpaca para {ticker}")
            
        barras.rename(columns={'close': 'Close', 'volume': 'Volume'}, inplace=True)
        df = barras[['Close', 'Volume']].copy()
        
        df['Retorno'] = df['Close'].pct_change()
        df['Volatilidad'] = df['Close'].rolling(window=14).std()
        df['Media_Movil'] = df['Close'].rolling(window=14).mean()
        df['Target'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
        df = df.dropna()
        
        return df
    except Exception as e:
        print(f"⚠️ Error Alpaca (Brain) en {ticker}: {e}")
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
    
    modelo.fit(X.iloc[:-1], y.iloc[:-1])
    
    ultimo_dato = X.iloc[[-1]]
    probabilidad = modelo.predict_proba(ultimo_dato)[0][1] * 100
    prediccion = int(modelo.predict(ultimo_dato)[0])
    precio_actual = df['Close'].iloc[-1]
    
    return prediccion, precio_actual, probabilidad