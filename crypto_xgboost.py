import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import crypto_brain

def calcular_indicadores_flash(df):
    """
    Inyecta telemetría matemática avanzada: Aceleración, Volumen y Memoria Secuencial.
    """
    # 1. RSI (Índice de Fuerza Relativa)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # 2. Bandas de Bollinger
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    df['STD_20'] = df['close'].rolling(window=20).std()
    df['Band_Upper'] = df['SMA_20'] + (df['STD_20'] * 2)
    df['Band_Lower'] = df['SMA_20'] - (df['STD_20'] * 2)

    # 3. MACD (Aceleración y Momentum)
    ema_12 = df['close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema_12 - ema_26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal'] # La verdadera fuerza del movimiento

    # 4. VROC (Volume Rate of Change) - Detecta inyecciones de liquidez de Ballenas
    df['Vol_ROC'] = df['volume'].pct_change(periods=3) * 100

    # 5. Vectores de Memoria (Lags) - ¿Qué pasó en las últimas 3 horas?
    df['Lag_1_Close'] = df['close'].shift(1)
    df['Lag_2_Close'] = df['close'].shift(2)
    df['Lag_1_Vol'] = df['volume'].shift(1)

    # 🎯 TARGET: 1 si la próxima vela sube, 0 si cae.
    df['Target'] = (df['close'].shift(-1) > df['close']).astype(int)

    # Limpiamos todos los valores nulos generados por los cálculos
    df.dropna(inplace=True)
    return df

def entrenar_nodo_beta(simbolo='BTC/USDT'):
    print(f"🧠 [IA CRIPTO V2] Iniciando entrenamiento Avanzado para {simbolo}...")
    
    df_crudo = crypto_brain.obtener_historico_cripto(simbolo, '1h', 1000)
    
    if df_crudo.empty:
        return
        
    df_limpio = calcular_indicadores_flash(df_crudo)
    
    # Hemos duplicado los sensores de la red neuronal
    features = ['open', 'high', 'low', 'close', 'volume', 'variacion_pct', 
                'RSI', 'SMA_20', 'Band_Upper', 'Band_Lower', 
                'MACD', 'MACD_Signal', 'MACD_Hist', 'Vol_ROC',
                'Lag_1_Close', 'Lag_2_Close', 'Lag_1_Vol']
                
    X = df_limpio[features]
    y = df_limpio['Target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, shuffle=False)

    print(f"⚙️ Procesando {len(X_train)} horas de entrenamiento y {len(X_test)} horas de validación...")

    # Ajustamos los hiperparámetros para procesar la nueva complejidad sin sobreajuste (overfitting)
    modelo = xgb.XGBClassifier(
        n_estimators=250, 
        learning_rate=0.01, 
        max_depth=5, 
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='logloss'
    )
    
    modelo.fit(X_train, y_train)

    predicciones = modelo.predict(X_test)
    precision = accuracy_score(y_test, predicciones)

    print("-" * 50)
    print(f"✅ ENTRENAMIENTO V2 COMPLETADO.")
    print(f"🎯 Precisión en datos no vistos (Últimas {len(X_test)} horas): {precision*100:.2f}%")
    print("-" * 50)

    nombre_archivo = f"modelo_cripto_{simbolo.replace('/', '')}.pkl"
    joblib.dump(modelo, nombre_archivo)
    print(f"💾 Cerebro avanzado guardado en disco: {nombre_archivo}")

if __name__ == "__main__":
    entrenar_nodo_beta('BTC/USDT')