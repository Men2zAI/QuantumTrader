import yfinance as yf
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import precision_score
import joblib
import os
import warnings
import optuna

warnings.filterwarnings('ignore')
optuna.logging.set_verbosity(optuna.logging.WARNING) # Mantenemos la consola limpia

def crear_features(df, tipo="ticker"):
    """
    Motor V7: Inyección Volumétrica y Sensores Macro.
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
        # Sensores Clásicos
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
        
        # ATR (Volatilidad)
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        df['ATR'] = ranges.max(axis=1).rolling(14).mean()

        # 🌊 NUEVOS SENSORES DE PRESIÓN INSTITUCIONAL (VOLUMEN) 🌊
        # 1. OBV (On-Balance Volume)
        df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
        
        # 2. VWAP Móvil (Precio Promedio Ponderado por Volumen de 14 días)
        precio_tipico = (df['High'] + df['Low'] + df['Close']) / 3
        df['VWAP_14'] = (precio_tipico * df['Volume']).rolling(window=14).sum() / df['Volume'].rolling(window=14).sum()
        df['Distancia_VWAP'] = (df['Close'] - df['VWAP_14']) / df['VWAP_14']

        # OBJETIVO DINÁMICO
        df['Max_5d'] = df['High'].rolling(window=5).max().shift(-5)
        meta_dinamica = df['Close'] + (df['ATR'] * 1.5)
        df['Target'] = (df['Max_5d'] >= meta_dinamica).astype(int)
        
        # Matriz expandida
        features_ticker = ['Retorno', 'RSI', 'MACD_Hist', 'Distancia_BB_Inf', 'ATR', 'SMA_20', 'SMA_50', 'OBV', 'Distancia_VWAP', 'Target']
        return df[features_ticker]

def entrenar_modelo_robusto(ticker):
    print(f"📥 {ticker}: Descargando datos masivos e inyectando sensores de volumen...")
    
    df_ticker = yf.Ticker(ticker).history(period="5y", interval="1d")
    df_qqq = yf.Ticker("QQQ").history(period="5y", interval="1d")
    df_vix = yf.Ticker("^VIX").history(period="5y", interval="1d")
    
    if df_ticker.empty or df_qqq.empty or df_vix.empty:
        print(f"⚠️ Error en la descarga de datos.")
        return
        
    df_ticker.index = pd.to_datetime(df_ticker.index).tz_localize(None).normalize()
    df_qqq.index = pd.to_datetime(df_qqq.index).tz_localize(None).normalize()
    df_vix.index = pd.to_datetime(df_vix.index).tz_localize(None).normalize()
        
    feat_ticker = crear_features(df_ticker, tipo="ticker")
    feat_qqq = crear_features(df_qqq, tipo="qqq")
    feat_vix = crear_features(df_vix, tipo="vix")
    
    df_unido = feat_ticker.join(feat_qqq, how='inner').join(feat_vix, how='inner').dropna()
    df_unido = df_unido.sort_index()
    
    X = df_unido.drop('Target', axis=1)
    y = df_unido['Target']
    
    split_idx = int(len(df_unido) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    balance_peso = (len(y_train) - y_train.sum()) / y_train.sum() if y_train.sum() > 0 else 1
    tscv = TimeSeriesSplit(n_splits=3)
    
    print("🧠 Iniciando Red Neuronal Bayesiana (Optuna) para calibración perfecta...")
    
    # LA MAGIA DE OPTUNA: La IA busca su propia configuración óptima
    def objective(trial):
        param = {
            'n_estimators': trial.suggest_int('n_estimators', 100, 300),
            'max_depth': trial.suggest_int('max_depth', 3, 7),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.2, log=True),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0)
        }
        
        xgb = XGBClassifier(**param, scale_pos_weight=balance_peso, random_state=42, eval_metric='logloss')
        
        precisiones = []
        for train_idx, val_idx in tscv.split(X_train):
            X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
            y_tr, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]
            
            xgb.fit(X_tr, y_tr)
            preds = xgb.predict(X_val)
            prec = precision_score(y_val, preds, zero_division=0)
            precisiones.append(prec)
            
        return np.mean(precisiones)

    # Creamos el estudio y le damos 20 iteraciones de evolución
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=20)
    
    # Entrenamos el modelo final con los mejores parámetros descubiertos
    mejor_modelo = XGBClassifier(**study.best_params, scale_pos_weight=balance_peso, random_state=42, eval_metric='logloss')
    mejor_modelo.fit(X_train, y_train)
    
    print("\n📊 EVALUANDO MODO FRANCOTIRADOR V7 (Volumen + Bayesiano)...")
    probabilidades = mejor_modelo.predict_proba(X_test)[:, 1] 
    
    for umbral in [0.50, 0.55, 0.60, 0.65]:
        predicciones_estrictas = (probabilidades >= umbral).astype(int)
        precision = precision_score(y_test, predicciones_estrictas, zero_division=0)
        cantidad_compras = predicciones_estrictas.sum()
        print(f"   ➤ Exigiendo {umbral*100:.0f}% -> PRECISIÓN: {precision*100:.2f}% (Balas: {cantidad_compras})")
    
    if not os.path.exists('modelos'):
        os.makedirs('modelos')
    
    nombre_archivo = f"modelos/modelo_{ticker}.pkl"
    joblib.dump(mejor_modelo, nombre_archivo)
    print(f"💾 Titán guardado: {nombre_archivo}\n" + "="*50)

if __name__ == "__main__":
    empresas_completas = ["NVDA", "AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "META", "NFLX", 
                          "AMD", "INTC", "PYPL", "ADBE", "CSCO", "PEP", "COST", "AVGO", 
                          "QCOM", "TMUS", "TXN", "AMAT"]
                          
    print(f"🚀 INICIANDO FORJA V7 PARA {len(empresas_completas)} ACTIVOS...")
    for empresa in empresas_completas:
        entrenar_modelo_robusto(empresa)