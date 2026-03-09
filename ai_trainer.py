import yfinance as yf
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.metrics import classification_report, precision_score
import joblib
import os
import warnings

warnings.filterwarnings('ignore')

def crear_features(df, tipo="ticker"):
    """
    Motor de Ingeniería de Características V6: Multicanal.
    """
    df['Retorno'] = df['Close'].pct_change()
    
    if tipo == "qqq":
        # 🌊 LA MAREA (Dirección del mercado tecnológico)
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['QQQ_Tendencia'] = np.where(df['Close'] > df['SMA_50'], 1, -1)
        df['QQQ_Retorno'] = df['Retorno']
        return df[['QQQ_Tendencia', 'QQQ_Retorno']]
        
    elif tipo == "vix":
        # ⚠️ EL SENSOR DEL MIEDO (Volatilidad global)
        df['VIX_Nivel'] = df['Close']
        df['VIX_Retorno'] = df['Retorno']
        return df[['VIX_Nivel', 'VIX_Retorno']]
        
    else:
        # ⛵ EL BOTE (Sensores técnicos de la empresa)
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

        # OBJETIVO DINÁMICO
        df['Max_5d'] = df['High'].rolling(window=5).max().shift(-5)
        meta_dinamica = df['Close'] + (df['ATR'] * 1.5)
        df['Target'] = (df['Max_5d'] >= meta_dinamica).astype(int)
        
        features_ticker = ['Retorno', 'RSI', 'MACD_Hist', 'Distancia_BB_Inf', 'ATR', 'SMA_20', 'SMA_50', 'Target']
        return df[features_ticker]

def entrenar_modelo_robusto(ticker):
    print(f"📥 Descargando {ticker}, Marea (QQQ) y Pánico (VIX)...")
    
    df_ticker = yf.Ticker(ticker).history(period="5y", interval="1d")
    df_qqq = yf.Ticker("QQQ").history(period="5y", interval="1d")
    df_vix = yf.Ticker("^VIX").history(period="5y", interval="1d")
    
    if df_ticker.empty or df_qqq.empty or df_vix.empty:
        print(f"⚠️ Error en la descarga de datos.")
        return
        
    # ⏱️ SINCRONIZACIÓN DE SENSORES: Eliminamos zonas horarias para un cruce perfecto
    df_ticker.index = pd.to_datetime(df_ticker.index).tz_localize(None).normalize()
    df_qqq.index = pd.to_datetime(df_qqq.index).tz_localize(None).normalize()
    df_vix.index = pd.to_datetime(df_vix.index).tz_localize(None).normalize()
        
    print("⚙️ Fusionando red de sensores (Micro + Macro + Miedo)...")
    feat_ticker = crear_features(df_ticker, tipo="ticker")
    feat_qqq = crear_features(df_qqq, tipo="qqq")
    feat_vix = crear_features(df_vix, tipo="vix")
    
    # Unificamos todo usando la fecha exacta como ancla
    df_unido = feat_ticker.join(feat_qqq, how='inner').join(feat_vix, how='inner').dropna()
    df_unido = df_unido.sort_index()
    
    X = df_unido.drop('Target', axis=1)
    y = df_unido['Target']
    
    casos_exito = y.sum()
    print(f"🔍 Casos de éxito detectados (Target=1): {casos_exito} de {len(y)} días.")
    
    # Corte secuencial estricto: 80% pasado, 20% futuro
    split_idx = int(len(df_unido) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    balance_peso = (len(y_train) - y_train.sum()) / y_train.sum() if y_train.sum() > 0 else 1
    
    print("🧠 Afinación Evolutiva con Validación Walk-Forward (TimeSeriesSplit)...")
    tscv = TimeSeriesSplit(n_splits=3)
    
    param_grid = {
        'n_estimators': [100, 200], 
        'max_depth': [3, 5],      
        'learning_rate': [0.01, 0.1] 
    }
    
    xgb = XGBClassifier(scale_pos_weight=balance_peso, random_state=42, eval_metric='logloss')
    grid_search = GridSearchCV(estimator=xgb, param_grid=param_grid, cv=tscv, scoring='precision', n_jobs=-1)
    
    grid_search.fit(X_train, y_train)
    mejor_modelo = grid_search.best_estimator_
    
    print("\n📊 EVALUANDO MODO FRANCOTIRADOR V6...")
    probabilidades = mejor_modelo.predict_proba(X_test)[:, 1] 
    
    umbrales_prueba = [0.50, 0.55, 0.60, 0.65]
    
    for umbral in umbrales_prueba:
        predicciones_estrictas = (probabilidades >= umbral).astype(int)
        precision = precision_score(y_test, predicciones_estrictas, zero_division=0)
        cantidad_compras = predicciones_estrictas.sum()
        
        print(f"   ➤ Exigiendo {umbral*100:.0f}% de confianza -> PRECISIÓN: {precision*100:.2f}% (Balas disparadas: {cantidad_compras})")
    
    if not os.path.exists('modelos'):
        os.makedirs('modelos')
    
    nombre_archivo = f"modelos/modelo_{ticker}.pkl"
    joblib.dump(mejor_modelo, nombre_archivo)
    print(f"\n💾 Cerebro de élite guardado: {nombre_archivo}\n" + "="*50)

if __name__ == "__main__":
    empresas_prueba = ["MSFT", "PYPL", "NVDA"]
    for empresa in empresas_prueba:
        entrenar_modelo_robusto(empresa)