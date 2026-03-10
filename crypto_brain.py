import ccxt
import pandas as pd

# CAMBIO DE NODO: KuCoin es "GitHub-friendly"
# Usamos KuCoin porque no bloquea los servidores de Microsoft Azure
nodo_exchange = ccxt.kucoin({
    'enableRateLimit': True,
})

def obtener_historico_cripto(simbolo='BTC/USDT', marco_tiempo='1h', limite=1000):
    print(f"📡 [MEMORIA CRIPTO] Interceptando {simbolo} vía KuCoin...")
    try:
        # La sintaxis de CCXT es idéntica, el resto del código no cambia
        velas = nodo_exchange.fetch_ohlcv(simbolo, timeframe=marco_tiempo, limit=limite)
        df = pd.DataFrame(velas, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['variacion_pct'] = df['close'].pct_change() * 100
        return df
    except Exception as e:
        print(f"⚠️ Error de red en el nodo: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Prueba de diagnóstico: Extraer las últimas 1000 horas de Bitcoin
    datos_historicos = obtener_historico_cripto('BTC/USDT', '1h', 1000)