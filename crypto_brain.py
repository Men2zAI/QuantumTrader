import ccxt
import pandas as pd

# Conexión al enjambre
nodo_binance = ccxt.binance({
    'enableRateLimit': True,
})

def obtener_historico_cripto(simbolo='BTC/USDT', marco_tiempo='1h', limite=1000):
    """
    Descarga la memoria OHLCV (Velas japonesas) desde la red de Binance.
    marco_tiempo: '1m', '5m', '15m', '1h', '4h', '1d'
    """
    print(f"📡 [MEMORIA CRIPTO] Descargando {limite} velas de {simbolo} en marco de {marco_tiempo}...")
    
    try:
        # Petición a la API cruda
        velas = nodo_binance.fetch_ohlcv(simbolo, timeframe=marco_tiempo, limit=limite)
        
        # Estructuramos los datos en un DataFrame de Pandas (Formato de Machine Learning)
        df = pd.DataFrame(velas, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Convertimos el timestamp de milisegundos a formato de fecha legible
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Añadimos indicadores básicos para el escaneo de red
        df['variacion_pct'] = df['close'].pct_change() * 100
        
        print(f"✅ Descarga completada. Filas estructuradas: {len(df)}")
        print("-" * 50)
        # Imprimimos las últimas 3 horas para confirmar
        print(df.tail(3).to_string(index=False))
        print("-" * 50)
        
        return df

    except Exception as e:
        print(f"⚠️ Error extrayendo memoria de la red: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Prueba de diagnóstico: Extraer las últimas 1000 horas de Bitcoin
    datos_historicos = obtener_historico_cripto('BTC/USDT', '1h', 1000)