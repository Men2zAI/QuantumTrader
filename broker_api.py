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
    Ejecuta compras usando Notional Trading (Dólares en lugar de Acciones enteras).
    Ideal para escalar operaciones con capitales reducidos.
    """
    if not alpaca:
        return "ERROR_API"

    try:
        # Redondear el monto de inversión a 2 decimales (ej. $23.01)
        monto_redondeado = round(monto_inversion, 2)
        
        # Disparar misil: Orden de Compra a Mercado en modo Fraccionario
        orden = alpaca.submit_order(
            symbol=ticker,
            notional=monto_redondeado,
            side='buy',
            type='market',
            time_in_force='day' # Alpaca exige 'day' para operaciones notional
        )
        
        print(f"🎯 [BROKER] ORDEN ENVIADA: Invirtiendo ${monto_redondeado} en {ticker} (Acción Fraccionaria).")
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