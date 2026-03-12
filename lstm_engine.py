import numpy as np
import pandas as pd
import yfinance as yf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
import requests # <-- NUEVO MÓDULO DE CAMUFLAJE

def analizar_onda(ticker):
    try:
        # --- INYECCIÓN DE CAMUFLAJE DE RED ---
        sesion_camuflada = requests.Session()
        sesion_camuflada.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        })
        
        df = yf.download(ticker, period="100d", progress=False, session=sesion_camuflada)
        if df.empty or len(df) < 60:
            return 0.50 

        data = df['Close'].values.reshape(-1, 1)
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data)

        X, y = [], []
        window = 10
        for i in range(window, len(scaled_data)):
            X.append(scaled_data[i-window:i, 0])
            y.append(scaled_data[i, 0])
            
        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))

        # Red LSTM Ultra-Ligera
        model = Sequential()
        model.add(LSTM(20, return_sequences=False, input_shape=(X.shape[1], 1)))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        
        # Entrenamiento relámpago
        model.fit(X, y, batch_size=16, epochs=5, verbose=0)

        # Predicción del próximo precio
        last_window = scaled_data[-window:]
        last_window = np.reshape(last_window, (1, window, 1))
        prediccion_escalada = model.predict(last_window, verbose=0)
        precio_proyectado = scaler.inverse_transform(prediccion_escalada)[0][0]
        
        precio_actual = df['Close'].iloc[-1]
        
        if precio_proyectado > precio_actual:
            return 0.65 
        else:
            return 0.35 
            
    except Exception as e:
        print(f"⚠️ LSTM Error ({ticker}): {e}")
        return 0.50