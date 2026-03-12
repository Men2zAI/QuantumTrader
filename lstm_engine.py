import os
import numpy as np
import pandas as pd
import alpaca_trade_api as tradeapi
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
alpaca = tradeapi.REST(
    os.getenv('ALPACA_API_KEY'), 
    os.getenv('ALPACA_SECRET_KEY'), 
    'https://paper-api.alpaca.markets', 
    api_version='v2'
)

def analizar_onda(ticker):
    try:
        fin = datetime.now() - timedelta(minutes=16) # Bypass SIP
        inicio = fin - timedelta(days=150)
        
        barras = alpaca.get_bars(
            ticker, 
            tradeapi.rest.TimeFrame.Day, 
            start=inicio.strftime('%Y-%m-%d'), 
            end=fin.strftime('%Y-%m-%d'),
            feed='iex'
        ).df
        
        if barras.empty or len(barras) < 60:
            return 0.50 

        data = barras['close'].values.reshape(-1, 1)
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data)

        X, y = [], []
        window = 10
        for i in range(window, len(scaled_data)):
            X.append(scaled_data[i-window:i, 0])
            y.append(scaled_data[i, 0])
            
        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))

        model = Sequential()
        model.add(LSTM(20, return_sequences=False, input_shape=(X.shape[1], 1)))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        
        model.fit(X, y, batch_size=16, epochs=5, verbose=0)

        last_window = scaled_data[-window:]
        last_window = np.reshape(last_window, (1, window, 1))
        prediccion_escalada = model.predict(last_window, verbose=0)
        precio_proyectado = scaler.inverse_transform(prediccion_escalada)[0][0]
        
        precio_actual = barras['close'].iloc[-1]
        
        return 0.65 if precio_proyectado > precio_actual else 0.35
            
    except Exception as e:
        print(f"⚠️ LSTM Error ({ticker}): {e}")
        return 0.50