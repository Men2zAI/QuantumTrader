import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import joblib
import os
import time
from datetime import datetime
from dotenv import load_dotenv
import notifier  # 🔌 CONECTANDO EL MÓDULO DE COMUNICACIONES

# Parámetros Globales
SIMBOLO = "EURUSD"
TIMEFRAME = mt5.TIMEFRAME_M15
VOLUMEN_LOTE = 0.01
UMBRAL_COMPRA = 0.60  # 60% de seguridad para disparar

def conectar_mt5():
    load_dotenv()
    login_id = int(os.getenv("MT5_LOGIN", 0))
    password = os.getenv("MT5_PASS", "")
    servidor = os.getenv("MT5_SERVER", "MetaQuotes-Demo")
    
    if not mt5.initialize():
        print("❌ Error de inicialización MT5")
        return False
    return mt5.login(login=login_id, password=password, server=servidor)

def obtener_datos_actuales():
    velas = mt5.copy_rates_from_pos(SIMBOLO, TIMEFRAME, 0, 50)
    if velas is None: return None
        
    df = pd.DataFrame(velas)
    df['Retorno'] = df['close'].pct_change()
    
    delta = df['close'].diff()
    ganancia = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    perdida = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = ganancia / (perdida + 1e-9)
    df['RSI'] = 100 - (100 / (1 + rs))
    
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    df['Volatilidad'] = df['close'].rolling(window=20).std()
    
    df.dropna(inplace=True)
    return df

def ejecutar_orden(tipo_orden):
    """Actuador blindado que ahora devuelve el precio de ejecución para Telegram"""
    precio = mt5.symbol_info_tick(SIMBOLO).ask if tipo_orden == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(SIMBOLO).bid
    modos_llenado = [mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_RETURN]
    
    for filling in modos_llenado:
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": SIMBOLO,
            "volume": VOLUMEN_LOTE,
            "type": tipo_orden,
            "price": precio,
            "deviation": 20,
            "magic": 777777,
            "comment": "IA Gamma V1",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling,
        }
        
        resultado = mt5.order_send(request)
        if resultado.retcode == mt5.TRADE_RETCODE_DONE:
            accion = "COMPRA" if tipo_orden == mt5.ORDER_TYPE_BUY else "VENTA"
            print(f"✅ ¡{accion} EJECUTADA! Ticket: {resultado.order} | Precio: {resultado.price}")
            return resultado.price  # 👈 Retornamos el precio real
            
    print("❌ Error: No se pudo ejecutar la orden en ningún modo de llenado.")
    return None  # 👈 Retornamos Nada si falla

def ciclo_orquestador():
    if not conectar_mt5():
        return
        
    try:
        df = obtener_datos_actuales()
        if df is None or df.empty:
            print("⚠️ No se pudieron obtener datos del mercado.")
            return
            
        features = ['Retorno', 'RSI', 'Volatilidad']
        X_actual = df[features].iloc[[-1]]
        
        ruta_modelo = f'modelos_gamma/xgb_{SIMBOLO}.pkl'
        if not os.path.exists(ruta_modelo):
            print("⚠️ Cerebro no encontrado. Ejecuta gamma_brain.py primero.")
            return
            
        modelo = joblib.load(ruta_modelo)
        probabilidad_alcista = modelo.predict_proba(X_actual)[0][1]
        
        print("-" * 40)
        print(f"📊 Análisis {SIMBOLO} | Velas 15M")
        print(f"📈 Probabilidad Alcista: {probabilidad_alcista * 100:.2f}%")
        
        # 4. Toma de Decisiones y Notificaciones 📱
        if probabilidad_alcista >= UMBRAL_COMPRA:
            print("🎯 Señal de COMPRA táctica detectada. Disparando...")
            precio_ejecutado = ejecutar_orden(mt5.ORDER_TYPE_BUY)
            
            if precio_ejecutado:
                msg = (f"🌍 *NODO GAMMA (FOREX)* 🌍\n"
                       f"⚡ Acción: COMPRA (Long)\n"
                       f"📊 Par: {SIMBOLO}\n"
                       f"🧠 Confianza IA: {probabilidad_alcista * 100:.2f}%\n"
                       f"💰 Precio: {precio_ejecutado}\n"
                       f"📦 Lotes: {VOLUMEN_LOTE}")
                notifier.enviar_telegram(msg)

        elif probabilidad_alcista <= (1 - UMBRAL_COMPRA):
            print("🎯 Señal de VENTA táctica detectada. Disparando...")
            precio_ejecutado = ejecutar_orden(mt5.ORDER_TYPE_SELL)
            
            if precio_ejecutado:
                prob_baja = (1 - probabilidad_alcista) * 100
                msg = (f"🌍 *NODO GAMMA (FOREX)* 🌍\n"
                       f"⚡ Acción: VENTA (Short)\n"
                       f"📊 Par: {SIMBOLO}\n"
                       f"🧠 Confianza IA: {prob_baja:.2f}%\n"
                       f"💰 Precio: {precio_ejecutado}\n"
                       f"📦 Lotes: {VOLUMEN_LOTE}")
                notifier.enviar_telegram(msg)
        else:
            print("⏳ Mercado en zona de ruido. Manteniendo capital a salvo.")
        print("-" * 40)
        
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    print("🤖 [NODO GAMMA] Activando modo Centinela Continuo (24/5)...")
    print("Presiona Ctrl+C en la terminal para apagar el motor.")
    
    while True:
        ahora = datetime.now()
        print(f"\n[{ahora.strftime('%H:%M:%S')}] Despertando sensores para escaneo táctico...")
        
        ciclo_orquestador()
        
        print("💤 Escaneo completado. Hibernando por 15 minutos para esperar la siguiente vela...")
        time.sleep(900)