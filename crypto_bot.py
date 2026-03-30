import pandas as pd
import joblib
import os
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
import crypto_brain
import crypto_xgboost
import requests

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MODELO_FILE = "modelo_cripto_BTCUSDT.pkl"
LOG_FINANCIERO = "crypto_balance.csv"

# ⚙️ PARÁMETROS DCA (Gestión de Riesgo Avanzada)
DCA_FRACTION = 0.02      # 2% del capital en DCA (Acumulación lenta)
TACTICAL_FRACTION = 0.10 # 10% del capital en Compra Fuerte

def registrar_operacion_virtual(precio, señal, inversion_usdt=0):
    """Fase B V2: Simulador Matemático Real con Bóveda BTC"""
    try:
        if not os.path.exists(LOG_FINANCIERO):
            df_bal = pd.DataFrame(columns=['timestamp', 'balance_usdt', 'balance_btc', 'activo', 'operacion', 'precio_ejecucion', 'monto_invertido'])
            df_bal.loc[0] = [datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 10000.0, 0.0, 'CASH', 'START', 0.0, 0.0]
        else:
            df_bal = pd.read_csv(LOG_FINANCIERO)
            # Compatibilidad: Añadimos columnas si vienes de la versión anterior
            if 'balance_btc' not in df_bal.columns:
                df_bal['balance_btc'] = 0.0
            if 'monto_invertido' not in df_bal.columns:
                df_bal['monto_invertido'] = 0.0

        ultima_fila = df_bal.iloc[-1]
        usdt_actual = float(ultima_fila['balance_usdt'])
        btc_actual = float(ultima_fila['balance_btc'])

        # Matemáticas de Ejecución (V10.3 - Bidireccional)
        if señal == "SELL_ALL" and btc_actual > 0:
            # 💰 COSECHA: Vender todo el BTC y sumarlo al USDT
            usdt_obtenido = btc_actual * precio
            usdt_final = usdt_actual + usdt_obtenido
            btc_final = 0.0
            inversion_usdt = usdt_obtenido # Registramos cuánto dinero recuperamos
            
        elif inversion_usdt > 0 and usdt_actual >= inversion_usdt:
            # 🟢 COMPRA: Restar USDT y sumar BTC
            usdt_final = usdt_actual - inversion_usdt
            btc_comprado = inversion_usdt / precio
            btc_final = btc_actual + btc_comprado
            
        else:
            # 🔴 ESPERA: No hacer nada
            inversion_usdt = 0.0
            usdt_final = usdt_actual
            btc_final = btc_actual
            if señal not in ["SELL_OR_WAIT", "START"]:
                señal = "WAIT_INSUFFICIENT_FUNDS"

        nuevo_registro = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'balance_usdt': round(usdt_final, 2),
            'balance_btc': round(btc_final, 6),
            'activo': 'BTC',
            'operacion': señal,
            'precio_ejecucion': precio,
            'monto_invertido': round(inversion_usdt, 2)
        }
        
        df_bal = pd.concat([df_bal, pd.DataFrame([nuevo_registro])], ignore_index=True)
        df_bal.to_csv(LOG_FINANCIERO, index=False)
        return inversion_usdt, usdt_final, btc_final
    except Exception as e:
        print(f"⚠️ Error contable: {e}")
        return 0, 0, 0

def enviar_telegram(mensaje):
    if not TELEGRAM_TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"})
    except: pass

try:
    cerebro = joblib.load(MODELO_FILE)
except:
    print("❌ Archivo de cerebro no encontrado. Verifica modelo_cripto_BTCUSDT.pkl")
    exit()

def calcular_atr(df, periodos=14):
    high_low = df['high'] - df['low']
    high_close = abs(df['high'] - df['close'].shift())
    low_close = abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    return true_range.rolling(periodos).mean().iloc[-1]

def ejecutar_escaneo_tiempo_real(simbolo='BTC/USDT'):
    print("🚀 INICIANDO NODO BETA (PROTOCOLOS DCA ACTIVADOS)...")
    df_reciente = crypto_brain.obtener_historico_cripto(simbolo, '1h', 50)
    if df_reciente.empty: return
        
    df_procesado = crypto_xgboost.calcular_indicadores_flash(df_reciente.copy())
    ultima_fila = df_procesado.iloc[-1:]
    
    features = ['open', 'high', 'low', 'close', 'volume', 'variacion_pct', 
                'RSI', 'SMA_20', 'Band_Upper', 'Band_Lower', 
                'MACD', 'MACD_Signal', 'MACD_Hist', 'Vol_ROC',
                'Lag_1_Close', 'Lag_2_Close', 'Lag_1_Vol']
                
    X_presente = ultima_fila[features]
    precio_actual = ultima_fila['close'].values[0]
    
    prob_subir = cerebro.predict_proba(X_presente)[0][1] * 100
    
    try:
        df_bal = pd.read_csv(LOG_FINANCIERO)
        usdt_disponible = float(df_bal.iloc[-1]['balance_usdt'])
    except:
        usdt_disponible = 10000.0

    inversion = 0.0
    estado = ""
    tipo_op = ""
    icono = ""

    # 🧠 LÓGICA DE DECISIÓN ESCALONADA (DCA V10.3 - Módulo Reaper Cripto)
    
    # 1. Calcular el Precio Promedio de Compra
    try:
        df_hist = pd.read_csv(LOG_FINANCIERO)
        btc_acumulado = float(df_hist.iloc[-1]['balance_btc'])
        compras = df_hist[df_hist['operacion'].isin(['BUY_TACTICAL', 'BUY_DCA'])]
        inversion_total = compras['monto_invertido'].sum()
        precio_promedio = (inversion_total / btc_acumulado) if btc_acumulado > 0 else 0
    except:
        btc_acumulado = 0.0
        precio_promedio = 0.0

    inversion = 0.0
    estado = ""
    tipo_op = ""
    icono = ""

    # 2. El Árbol de Decisiones
    # Si tenemos BTC y el precio actual es un 5% MAYOR que nuestro promedio de compra: ¡VENDER!
    if btc_acumulado > 0.0005 and precio_actual >= (precio_promedio * 1.05):
        estado = f"COSECHA DE GANANCIAS (+5% sobre ${precio_promedio:,.0f})"
        tipo_op = "SELL_ALL"
        icono = "💰"
        
    elif prob_subir >= 54.0:
        estado = "COMPRA TÁCTICA"
        tipo_op = "BUY_TACTICAL"
        inversion = usdt_disponible * TACTICAL_FRACTION
        icono = "🟢"
        
    elif prob_subir >= 48.0 and prob_subir < 54.0:
        estado = "ACUMULACIÓN DCA"
        tipo_op = "BUY_DCA"
        inversion = usdt_disponible * DCA_FRACTION
        icono = "💧"
        
    else:
        estado = "ESPERA / RIESGO DE CAÍDA"
        tipo_op = "SELL_OR_WAIT"
        inversion = 0.0
        icono = "🔴"

    monto_inv, usdt_restante, btc_acumulado = registrar_operacion_virtual(precio_actual, tipo_op, inversion)
    
    # 📱 NOTIFICACIÓN TELEGRAM REDISEÑADA
    mensaje_tg = (f"🤖 *NODO BETA* (Crypto V10.2)\n"
                  f"💰 *BTC:* ${precio_actual:,.2f}\n"
                  f"🧠 *Señal:* {icono} {estado} ({prob_subir:.1f}%)\n")
    
    if inversion > 0:
        mensaje_tg += (f"💸 *Invertido:* ${monto_inv:,.2f} USDT\n"
                       f"💼 *Caja Libre:* ${usdt_restante:,.2f} USDT\n"
                       f"🪙 *Bóveda BTC:* ₿{btc_acumulado:.6f}")
    else:
        mensaje_tg += f"\n💼 *Caja Intacta:* ${usdt_disponible:,.2f} USDT"

    enviar_telegram(mensaje_tg)
    print(mensaje_tg)

if __name__ == "__main__":
    ejecutar_escaneo_tiempo_real('BTC/USDT')