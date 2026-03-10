import ccxt
import pandas as pd
import time

# Inicializamos el nodo de conexión a Binance
# enableRateLimit=True es vital para que Binance no bloquee nuestra IP por exceso de peticiones
nodo_binance = ccxt.binance({
    'enableRateLimit': True,
})

def escanear_telemetria_cripto(simbolo='BTC/USDT'):
    print(f"🌐 [NODO BETA] Interceptando red de {simbolo} en Binance...")
    
    try:
        # 1. Extraer el ticker en tiempo real
        ticker = nodo_binance.fetch_ticker(simbolo)
        precio_actual = ticker['last']
        volumen_24h = ticker['baseVolume']
        
        # 2. Extraer la Profundidad del Mercado (Los próximos 5 niveles del libro de órdenes)
        order_book = nodo_binance.fetch_order_book(simbolo, limit=5)
        
        # Bids = Gente queriendo comprar (Soporte)
        mejor_comprador = order_book['bids'][0][0] if order_book['bids'] else 0
        vol_comprador = order_book['bids'][0][1] if order_book['bids'] else 0
        
        # Asks = Gente queriendo vender (Resistencia)
        mejor_vendedor = order_book['asks'][0][0] if order_book['asks'] else 0
        vol_vendedor = order_book['asks'][0][1] if order_book['asks'] else 0
        
        print("-" * 40)
        print(f"💰 Precio Actual : ${precio_actual:,.2f}")
        print(f"🌊 Volumen 24h   : {volumen_24h:,.2f} BTC")
        print("-" * 40)
        print(f"🧱 Muro de Venta  : ${mejor_vendedor:,.2f} (Vol: {vol_vendedor} BTC)")
        print(f"🟢 Muro de Compra : ${mejor_comprador:,.2f} (Vol: {vol_comprador} BTC)")
        print("-" * 40)
        
        # Margen (Spread) entre el comprador y el vendedor
        spread = mejor_vendedor - mejor_comprador
        print(f"📏 Spread de red  : ${spread:,.2f}")
        
    except Exception as e:
        print(f"⚠️ Error de conexión con el enjambre cripto: {e}")

if __name__ == "__main__":
    # Ejecutamos un escaneo rápido
    escanear_telemetria_cripto('BTC/USDT')
    
    # Si quieres escanear otra moneda, por ejemplo Ethereum:
    # escanear_telemetria_cripto('ETH/USDT')