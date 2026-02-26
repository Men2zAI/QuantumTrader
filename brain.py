import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

class TradingBrain:
    def __init__(self):
        # Simplificamos el bosque para que no se "pierda" en el ruido
        self.model = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)

    def prepare_features(self, df):
        df = df.copy()
        # Features Relativas (Estacionarias)
        df['Retorno_1d'] = df['Close'].pct_change()
        df['Volatilidad'] = df['Close'].rolling(window=10).std() / df['Close']
        
        # RSI Manual
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss)))
        
        return df.dropna()

    def train_predictive_model(self, df):
        # Objetivo: ¿Hacia dónde irá en 5 días?
        df['Target_Ret'] = df['Close'].shift(-5) / df['Close'] - 1
        df_train = df.dropna()
        
        features = ['Retorno_1d', 'Volatilidad', 'RSI']
        X = df_train[features]
        y = df_train['Target_Ret']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        self.model.fit(X_train, y_train)
        
        # --- NUEVA MÉTRICA: Precisión Direccional ---
        # ¿Cuántas veces el signo predicho coincide con el signo real?
        y_pred_test = self.model.predict(X_test)
        aciertos_dir = np.sign(y_pred_test) == np.sign(y_test)
        confianza_dir = np.mean(aciertos_dir)
        
        # Predicción Final
        last_features = X.tail(1)
        pred_array = self.model.predict(last_features)
        
        # .item() convierte un array de un solo elemento en un escalar puro de Python
        prediction_val = float(df['Close'].values[-1]) * (1 + pred_array.item())        
        return prediction_val, float(confianza_dir)