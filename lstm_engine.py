import numpy as np
import pandas as pd
import yfinance as yf
import os
import joblib
import warnings

# Ocultar advertencias y optimizar TensorFlow
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 

from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

# ⚙️ PARÁMETROS DE LA MATRIZ TEMPORAL
VENTANA_TIEMPO = 60  # La IA analizará la "película" de los últimos 60 días
DIAS_PREDICCION = 5
UMBRAL_ATR = 1.5

def preparar_datos_lstm(ticker):
    """
    Descarga y empaqueta la serie temporal en bloques 3D para la red neuronal.
    """
    df = yf.Ticker(ticker).history(period="5y", interval="1d")
    if df.empty: return None, None, None, None
    
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    
    # 1. Crear Sensores Básicos para la memoria
    df['Retorno'] = df['Close'].pct_change()
    df['Volumen'] = df['Volume']
    
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    df['ATR'] = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1).rolling(14).mean()
    
    df.dropna(inplace=True)
    
    # 2. Definir el Objetivo Dinámico (Igual que en XGBoost para mantener coherencia)
    df['Max_Futuro'] = df['High'].rolling(window=DIAS_PREDICCION).max().shift(-DIAS_PREDICCION)
    meta = df['Close'] + (df['ATR'] * UMBRAL_ATR)
    df['Target'] = (df['Max_Futuro'] >= meta).astype(int)
    
    # Nos quedamos con los datos limpios
    features = ['Close', 'Retorno', 'Volumen', 'ATR']
    dataset = df[features].values
    target = df['Target'].values[:-DIAS_PREDICCION] # Quitamos los últimos días sin futuro
    dataset = dataset[:-DIAS_PREDICCION]
    
    # 3. Normalización Matemática (CRÍTICO para Redes Neuronales)
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset_escalado = scaler.fit_transform(dataset)
    
    # 4. Creación de la Matriz 3D (Muestras, Ventana de Tiempo, Sensores)
    X, y = [], []
    for i in range(VENTANA_TIEMPO, len(dataset_escalado)):
        X.append(dataset_escalado[i-VENTANA_TIEMPO:i])
        y.append(target[i])
        
    return np.array(X), np.array(y), scaler, df

def entrenar_cerebro_lstm(ticker):
    print(f"\n📥 {ticker}: Forjando memoria profunda (TensorFlow)...")
    X, y, scaler, df = preparar_datos_lstm(ticker)
    
    if X is None or len(X) < 100:
        print(f"⚠️ Datos insuficientes para {ticker}.")
        return

    # Dividir entrenamiento (80%) y prueba (20%) cronológicamente
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # 🧠 ARQUITECTURA DE LA RED NEURONAL PROFUNDA
    print(f"⚙️ Compilando Red Neuronal Recurrente para {ticker}...")
    modelo = Sequential()
    
    # Capa LSTM 1: Extrae la forma de la onda
    modelo.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
    modelo.add(Dropout(0.2)) # Apaga neuronas aleatorias para evitar que se memorice el pasado (Overfitting)
    
    # Capa LSTM 2: Condensa la información
    modelo.add(LSTM(units=50, return_sequences=False))
    modelo.add(Dropout(0.2))
    
    # Capa de Salida: Una neurona que dispara una probabilidad (0 a 1)
    modelo.add(Dense(units=1, activation='sigmoid'))
    
    # Compilación con optimizador Adam
    modelo.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    
    # Entrenar la red (Epochs)
    print("🚀 Iniciando entrenamiento (Buscando patrones en el hiperespacio)...")
    # EarlyStopping detiene el entrenamiento si la IA deja de aprender
    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    
    modelo.fit(X_train, y_train, epochs=30, batch_size=32, validation_data=(X_test, y_test), callbacks=[early_stop], verbose=1)
    
    # Evaluar precisión final en datos no vistos
    loss, accuracy = modelo.evaluate(X_test, y_test, verbose=0)
    print(f"🎯 PRECISIÓN DE LA MEMORIA (LSTM): {accuracy*100:.2f}%")
    
    # Guardar la red neuronal y su escalador matemático
    if not os.path.exists('modelos_deep'):
        os.makedirs('modelos_deep')
        
    modelo.save(f"modelos_deep/lstm_{ticker}.h5")
    joblib.dump(scaler, f"modelos_deep/scaler_{ticker}.pkl")
    print(f"💾 Cerebro Deep Learning guardado: modelos_deep/lstm_{ticker}.h5")

from tensorflow.keras.models import load_model

def analizar_onda(ticker):
    """
    Sensor de Producción LSTM: Carga el tensor 3D de los últimos 60 días
    y consulta a la red neuronal profunda la probabilidad de continuación de tendencia.
    """
    ruta_modelo = f"modelos_deep/lstm_{ticker}.h5"
    ruta_scaler = f"modelos_deep/scaler_{ticker}.pkl"

    if not os.path.exists(ruta_modelo) or not os.path.exists(ruta_scaler):
        return 0.5  # Si no hay cerebro, devuelve neutralidad absoluta (50%)

    try:
        # Descargamos solo los últimos 100 días para tener datos suficientes para el ATR
        df = yf.Ticker(ticker).history(period="100d", interval="1d")
        if df.empty: return 0.5

        df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
        df['Retorno'] = df['Close'].pct_change()
        df['Volumen'] = df['Volume']

        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        df['ATR'] = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1).rolling(14).mean()

        df.dropna(inplace=True)

        features = ['Close', 'Retorno', 'Volumen', 'ATR']
        dataset = df[features].values

        # Necesitamos la película exacta de 60 días
        if len(dataset) < 60: return 0.5
        ultimos_60 = dataset[-60:]

        # Normalizar con el mismo escalador matemático del entrenamiento
        scaler = joblib.load(ruta_scaler)
        ultimos_60_escalado = scaler.transform(ultimos_60)

        # Crear el Tensor 3D (1 muestra, 60 días, 4 variables)
        X_produccion = np.array([ultimos_60_escalado])

        # Consultar al cerebro profundo
        modelo = load_model(ruta_modelo)
        probabilidad = modelo.predict(X_produccion, verbose=0)[0][0]

        return float(probabilidad)
    except Exception as e:
        print(f"⚠️ Error en sensor LSTM para {ticker}: {e}")
        return 0.5
if __name__ == "__main__":
    empresas_completas = ["NVDA", "AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "META", "NFLX", 
                          "AMD", "INTC", "PYPL", "ADBE", "CSCO", "PEP", "COST", "AVGO", 
                          "QCOM", "TMUS", "TXN", "AMAT"]
                          
    print(f"🚀 INICIANDO FORJA PROFUNDA (LSTM) PARA {len(empresas_completas)} ACTIVOS...")
    for empresa in empresas_completas:
        entrenar_cerebro_lstm(empresa)