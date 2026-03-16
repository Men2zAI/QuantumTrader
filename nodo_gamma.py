import MetaTrader5 as mt5
import pandas as pd
import os
from dotenv import load_dotenv

def conectar_mt5():
    load_dotenv()
    login_id = int(os.getenv("MT5_LOGIN", 0))
    password = os.getenv("MT5_PASS", "")
    servidor = os.getenv("MT5_SERVER", "MetaQuotes-Demo")
    
    if not mt5.initialize():
        print("❌ Error de inicialización MT5")
        return False
        
    return mt5.login(login=login_id, password=password, server=servidor)

def obtener_datos_divisa(simbolo="EURUSD", timeframe=mt5.TIMEFRAME_H1, num_velas=100):
    """
    Sensor de Mercado: Extrae velas históricas y las formatea para la IA.
    """
    print(f"📡 Descargando últimas {num_velas} velas de {simbolo}...")
    velas = mt5.copy_rates_from_pos(simbolo, timeframe, 0, num_velas)
    
    if velas is None:
        print(f"❌ Error al obtener datos de {simbolo}. Verifica que el símbolo exista en tu broker.")
        return pd.DataFrame()
        
    df = pd.DataFrame(velas)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    return df

def orden_prueba_micro(simbolo="EURUSD", volumen=0.01):
    """
    Actuador V2: Envía una orden de compra iterando sobre los 
    protocolos de llenado (Filling Modes) para evadir el Error 10030.
    """
    print(f"🎯 Preparando orden de COMPRA para {simbolo} (Volumen: {volumen} lotes)...")
    
    # Aseguramos que el símbolo esté visible en el Market Watch
    if not mt5.symbol_select(simbolo, True):
        print(f"❌ El broker no tiene habilitado el símbolo {simbolo}.")
        return

    # Obtener el precio actual de compra (Ask)
    precio_ask = mt5.symbol_info_tick(simbolo).ask
    
    # 🛡️ BYPASS ERROR 10030: Matriz de políticas de llenado
    modos_llenado = [mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_RETURN]
    
    for filling in modos_llenado:
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": simbolo,
            "volume": volumen,
            "type": mt5.ORDER_TYPE_BUY,
            "price": precio_ask,
            "deviation": 20, # Aumentamos tolerancia a 20 puntos
            "magic": 999999, # Firma digital de tu bot
            "comment": "Gamma Test V2",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling, # Intentamos el modo actual del bucle
        }
        
        resultado = mt5.order_send(request)
        
        # Si el broker acepta la orden, detenemos el bucle y celebramos
        if resultado.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"✅ ¡ORDEN EJECUTADA EN EL MAINFRAME! (Modo de Llenado: {filling})")
            print(f"🎫 Ticket de Operación: {resultado.order}")
            print(f"💰 Comprado a: {resultado.price}")
            return
            
        # Si el error es 10030, el bucle simplemente intentará el siguiente modo.
        # Si es un error distinto, detenemos y avisamos.
        elif resultado.retcode != 10030:
            print(f"❌ Orden rechazada por otro motivo. Código: {resultado.retcode}")
            return
            
    print("❌ Error 10030 persistente: Ningún modo de llenado fue aceptado por este broker.")

if __name__ == "__main__":
    if conectar_mt5():
        print("🌍 [NODO GAMMA] Conectado al Mainframe.")
        
        # Prueba 1: Lectura de Datos
        df_eurusd = obtener_datos_divisa("EURUSD", mt5.TIMEFRAME_H1, 5)
        if not df_eurusd.empty:
            print("\n📊 Muestra de datos extraídos (EUR/USD):")
            print(df_eurusd[['open', 'high', 'low', 'close']].tail(2))
        
        # Prueba 2: Actuador (Disparo al mercado)
        print("\n" + "-"*40)
        orden_prueba_micro("EURUSD", 0.01)
        print("-"*40)
        
        mt5.shutdown()