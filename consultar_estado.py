import pandas as pd
import os
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
from datetime import datetime

# 1. Configuración de Acceso a la Red
load_dotenv()
API_KEY = os.getenv('ALPACA_API_KEY')
SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
BASE_URL = 'https://api.alpaca.markets'

def obtener_resumen_global():
    # Sincronización de reloj local
    ahora = datetime.now()
    print(f"\n📡 [AUDITORÍA] Extrayendo telemetría de mercados ({ahora.strftime('%H:%M:%S')})...")
    
    # --- BLOQUE A: WALL STREET (ALPACA) ---
    # Calibración: Tu saldo neto inicial es $100,000.00 (Cash)
    SALDO_INICIAL_WS = 100000.0 
    
    try:
        alpaca = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')
        cuenta = alpaca.get_account()
        
        # Leemos el Equity (Patrimonio Neto = Efectivo + Valor de Acciones)
        saldo_ws = float(cuenta.equity)
        cambio_ws = saldo_ws - SALDO_INICIAL_WS
        ws_status = "🟢" if cambio_ws >= 0 else "🔴"
        ws_error = False
    except Exception as e:
        saldo_ws, cambio_ws, ws_status = 0.0, 0.0, "⚠️ ERROR"
        ws_error = f"Falla de conexión: {e}"

    # --- BLOQUE B: CRIPTO (MEMORIA DEL NODO BETA) ---
    # Calibración: Saldo inicial simulado de $10,000.00
    SALDO_INICIAL_CRIPTO = 10000.0
    ARCHIVO_LOG = "crypto_balance.csv"
    
    try:
        if os.path.exists(ARCHIVO_LOG):
            df_cripto = pd.read_csv(ARCHIVO_LOG)
            ultimo_registro = df_cripto.iloc[-1]
            saldo_cripto = float(ultimo_registro['balance_usdt'])
            cambio_cripto = saldo_cripto - SALDO_INICIAL_CRIPTO
            cripto_status = "🟢" if cambio_cripto >= 0 else "🔴"
        else:
            saldo_cripto, cambio_cripto, cripto_status = SALDO_INICIAL_CRIPTO, 0.0, "⚪"
    except Exception as e:
        saldo_cripto, cambio_cripto, cripto_status = 0.0, 0.0, "⚠️ ERROR"

    # --- CÁLCULO DE PATRIMONIO CONSOLIDADO ---
    total_patrimonio = saldo_ws + saldo_cripto
    beneficio_neto = cambio_ws + cambio_cripto

    # --- RENDERIZADO DEL PANEL DE CONTROL ---
    print("="*50)
    print(f"🌍 PANEL DE CONTROL CUÁNTICO - {ahora.strftime('%d/%m/%Y')}")
    print("="*50)
    
    # AQUÍ ESTÁ LA CORRECCIÓN: :,.2f sin paréntesis
    print(f"🇺🇸 WALL STREET:  ${saldo_ws:,.2f} {ws_status} ({cambio_ws:+,.2f})")
    print(f"₿  CRIPTO (BTC): ${saldo_cripto:,.2f} {cripto_status} ({cambio_cripto:+,.2f})")
    
    print("-" * 50)
    print(f"💰 PATRIMONIO TOTAL:  ${total_patrimonio:,.2f}")
    print(f"📈 RENDIMIENTO NETO:  ${beneficio_neto:+,.2f}")
    print("="*50)

    # Lógica de Estado de Mercado (CET Italia)
    hora_actual = ahora.hour
    minuto_actual = ahora.minute
    mercado_abierto = (hora_actual == 15 and minuto_actual >= 30) or (16 <= hora_actual < 22)

    if ws_error:
        print(f"❌ ALERTA ALPHA: {ws_error}")
    elif mercado_abierto:
        print(f"⏱️ ESTADO WS: Mercado ABIERTO (Transmisión en vivo)")
    else:
        print(f"⏱️ ESTADO WS: Mercado CERRADO (Análisis post-sesión)")
        
    print(f"🤖 ESTADO BETA: Vigilancia activa 24/7 vía KuCoin")
    print("="*50 + "\n")

if __name__ == "__main__":
    obtener_resumen_global()