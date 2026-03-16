import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import os

# Parámetros del Mainframe Gamma
SIMBOLO = "EURUSD"
TIMEFRAME = mt5.TIMEFRAME_M15  # Velas de 15 minutos (Táctico)
VELAS_HISTORICAS = 5000        # Mucha data para entrenar el árbol

def extraer_y_procesar_datos():
    """Sensor de extracción técnica para MT5"""
    print(f"📡 Extrayendo {VELAS_HISTORICAS} velas de {SIMBOLO}...")
    velas = mt5.copy_rates_from_pos(SIMBOLO, TIMEFRAME, 0, VELAS_HISTORICAS)
    
    if velas is None:
        print("❌ Error de extracción de datos.")
        return None
        
    df = pd.DataFrame(velas)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    
    # Ingeniería de Características (Indicadores Forex)
    df['Retorno'] = df['close'].pct_change()
    
    # RSI rápido (14 periodos)
    delta = df['close'].diff()
    ganancia = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    perdida = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = ganancia / (perdida + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Medias Móviles y Volatilidad
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    df['Volatilidad'] = df['close'].rolling(window=20).std()
    
    # Target: ¿El precio en la próxima vela de 15m será mayor?
    df['Target'] = np.where(df['close'].shift(-1) > df['close'], 1, 0)
    
    df.dropna(inplace=True)
    return df

def forjar_cerebro_xgboost():
    """Entrenamiento del núcleo predictivo"""
    df = extraer_y_procesar_datos()
    if df is None or df.empty: return
    
    features = ['Retorno', 'RSI', 'Volatilidad']
    X = df[features]
    y = df['Target']
    
    print("🧠 Forjando conexiones sinápticas (XGBoost Gamma)...")
    modelo = xgb.XGBClassifier(
        objective='binary:logistic',
        eval_metric='logloss',
        max_depth=4,
        learning_rate=0.05,
        n_estimators=150
    )
    
    # Entrenar excluyendo la última vela (que es el presente puro)
    modelo.fit(X.iloc[:-1], y.iloc[:-1])
    
    # Guardar el cerebro localmente
    if not os.path.exists('modelos_gamma'):
        os.makedirs('modelos_gamma')
    joblib.dump(modelo, f'modelos_gamma/xgb_{SIMBOLO}.pkl')
    print(f"✅ Cerebro Gamma guardado: modelos_gamma/xgb_{SIMBOLO}.pkl")

if __name__ == "__main__":
    # Importante: Asumimos que la conexión MT5 ya está abierta por el orquestador, 
    # pero para probarlo de forma independiente, inicializamos aquí.
    if mt5.initialize():
        forjar_cerebro_xgboost()
        mt5.shutdown()