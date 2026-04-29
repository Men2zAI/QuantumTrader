import alpaca_trade_api as tradeapi
import os
import math
from dotenv import load_dotenv

load_dotenv()

# 🔐 Conexión Segura al Broker
try:
    alpaca = tradeapi.REST(
        os.getenv('ALPACA_API_KEY'),
        os.getenv('ALPACA_SECRET_KEY'),
        os.getenv('ALPACA_BASE_URL'),
        api_version='v2'
    )
    print("🌐 [API BROKER] Conexión establecida con Alpaca Markets.")
except Exception as e:
    print(f"⚠️ [API BROKER] Error crítico de conexión: {e}")
    alpaca = None

def obtener_poder_adquisitivo():
    """Consulta el saldo real disponible en la cuenta del broker."""
    if not alpaca: return 0.0
    try:
        cuenta = alpaca.get_account()
        return float(cuenta.buying_power)
    except Exception as e:
        print(f"⚠️ Error leyendo saldo: {e}")
        return 0.0

def ejecutar_orden_mercado(ticker, monto_inversion, precio_actual):
    """
    Traduce el dinero calculado por Kelly en cantidad de acciones
    y dispara la orden directa al Exchange.
    """
    if not alpaca:
        return "ERROR_API"

    try:
        # Calcular cuántas acciones enteras podemos comprar
        cantidad_acciones = math.floor(monto_inversion / precio_actual)
        
        if cantidad_acciones <= 0:
            print(f"⚠️ {ticker}: Inversión insuficiente para comprar 1 acción entera.")
            return "FONDOS_INSUFICIENTES"

        # Disparar misil: Orden de Compra a Mercado
        orden = alpaca.submit_order(
            symbol=ticker,
            qty=cantidad_acciones,
            side='buy',
            type='market',
            time_in_force='gtc' # Good 'Til Canceled
        )
        
        print(f"🎯 [BROKER] ORDEN ENVIADA: Comprando {cantidad_acciones} acciones de {ticker}.")
        return "ORDEN_COMPLETADA"
        
    except Exception as e:
        print(f"⚠️ [BROKER] Rechazo en el Exchange para {ticker}: {e}")
        return "ORDEN_RECHAZADA"

def sincronizar_cartera():
    """Lee qué acciones tenemos compradas actualmente en Alpaca."""
    if not alpaca: return []
    try:
        posiciones = alpaca.list_positions()
        return [pos.symbol for pos in posiciones]
    except Exception as e:
        print(f"⚠️ Error sincronizando cartera: {e}")
        return []

if __name__ == "__main__":
    # Test de diagnóstico
    saldo = obtener_poder_adquisitivo()
    print(f"💰 Poder adquisitivo actual en Alpaca: ${saldo:.2f}")
    
    cartera = sincronizar_cartera()
    print(f"📂 Posiciones abiertas en el broker: {cartera}")