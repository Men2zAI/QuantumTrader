import brain
import lstm_engine
import nlp_engine
import options_engine  
import broker_api
import notifier
import logger_engine
import pandas as pd
import report_generator
import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv

load_dotenv()

EMPRESAS = ["NVDA", "AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "META", "NFLX", 
            "AMD", "INTC", "PYPL", "ADBE", "CSCO", "PEP", "COST", "AVGO", 
            "QCOM", "TMUS", "TXN", "AMAT", "PLTR", "COIN", "ARM"]

RATIO_R_B = 2.0
FRACCION_KELLY = 0.5

def calcular_kelly(probabilidad_ia):
    W = probabilidad_ia
    kelly_pct = W - ((1 - W) / RATIO_R_B)
    kelly_seguro = kelly_pct * FRACCION_KELLY
    if kelly_seguro <= 0: return 0.0
    return max(0.01, min(kelly_seguro, 0.15))

def ejecutar_reaper():
    """
    🪓 MÓDULO REAPER (V10.2): Toma de ganancias y corte de pérdidas automático.
    Escanea la cartera en vivo y liquida posiciones que toquen los umbrales.
    """
    print("\n🪓 Iniciando Módulo Reaper (Take Profit / Stop Loss)...")
    try:
        alpaca = tradeapi.REST(
            os.getenv('ALPACA_API_KEY'), 
            os.getenv('ALPACA_SECRET_KEY'), 
            'https://api.alpaca.markets', 
            api_version='v2'
        )
        posiciones = alpaca.list_positions()
        
        if not posiciones:
            print("📂 Cartera vacía. Nada que cosechar por ahora.")
            return

        for posicion in posiciones:
            ticker = posicion.symbol
            qty = posicion.qty
            # Extraemos el PnL (Ganancia/Pérdida) en porcentaje
            pnl_pct = float(posicion.unrealized_plpc) * 100 
            
            # Extraemos el precio actual para la contabilidad
            precio_actual = float(posicion.current_price)
            monto_recuperado = float(qty) * precio_actual

            # 🎯 UMBRALES DE SALIDA
            if pnl_pct >= 6.0:
                print(f"💰 TAKE PROFIT: {ticker} ha alcanzado +{pnl_pct:.2f}%. Liquidando posición.")
                alpaca.submit_order(symbol=ticker, qty=qty, side='sell', type='market', time_in_force='day')
                
                # NUEVO: Guardar en el CSV
                logger_engine.guardar_registro(ticker, precio_actual, "VENTA (+6% GANANCIA)", 100.0, monto_recuperado)
                
                msg = f"💰 *TAKE PROFIT EJECUTADO*\n📈 Activo: {ticker}\n✅ Ganancia: +{pnl_pct:.2f}%\n📦 Acciones Liquidadas: {qty}"
                notifier.enviar_telegram(msg)
                
            elif pnl_pct <= -3.0:
                print(f"🛡️ STOP LOSS: {ticker} ha caído a {pnl_pct:.2f}%. Cortando pérdidas.")
                alpaca.submit_order(symbol=ticker, qty=qty, side='sell', type='market', time_in_force='day')
                
                # NUEVO: Guardar en el CSV
                logger_engine.guardar_registro(ticker, precio_actual, "VENTA (-3% PÉRDIDA)", 0.0, monto_recuperado)
                
                msg = f"🛡️ *STOP LOSS EJECUTADO*\n📉 Activo: {ticker}\n❌ Pérdida: {pnl_pct:.2f}%\n📦 Acciones Liquidadas: {qty}"
                notifier.enviar_telegram(msg)
                
    except Exception as e:
        print(f"⚠️ Error en Módulo Reaper: {e}")

def ejecutar_analisis_dinamico():
    print("🚀 INICIANDO ORQUESTADOR V10.2 (REAPER + FUSIÓN CUÁDRUPLE)...")
    
    # 1. Ejecutar recolección de ganancias primero
    ejecutar_reaper()
    
    saldo_actual = broker_api.obtener_poder_adquisitivo()
    print(f"\n💰 Poder adquisitivo detectado: ${saldo_actual:.2f}")
    
    if saldo_actual < 100:
        print("⚠️ Capital insuficiente para operar.")
        return

    acciones_abiertas = broker_api.sincronizar_cartera()

    candidatos = []
    print("\n📡 Iniciando comité neuronal de cuádruple núcleo...")
    
    for empresa in EMPRESAS:
        if empresa in acciones_abiertas:
            print(f"⏳ {empresa}: Omitida (Ya en cartera).")
            continue
            
        try:
            # 🔌 LOS 4 SENSORES DE TELEMETRÍA
            df = brain.obtener_datos(empresa)
            _, precio, fiabilidad_xgb = brain.predecir(df, empresa)
            prob_nlp = nlp_engine.analizar_sentimiento(empresa)
            prob_lstm = lstm_engine.analizar_onda(empresa)
            prob_opciones = options_engine.analizar_opciones(empresa)
            
            # 🧠 META-APRENDIZ: Fusión Matemática en 4 Dimensiones
            prob_xgb_decimal = fiabilidad_xgb / 100.0
            prob_fusionada = (prob_xgb_decimal * 0.35) + (prob_lstm * 0.30) + (prob_opciones * 0.20) + (prob_nlp * 0.15)
            fiabilidad_final = round(prob_fusionada * 100, 2)
            
            if prob_fusionada >= 0.54:
                candidatos.append({
                    'ticker': empresa,
                    'precio': precio,
                    'señal': "COMPRA CUÁDRUPLE",
                    'fiabilidad': fiabilidad_final,
                    'prob_decimal': prob_fusionada
                })
                print(f"✅ {empresa}: ¡FUSIÓN V10! (Final: {fiabilidad_final}%)")
            else:
                print(f"   {empresa}: Descartada (Fusión: {fiabilidad_final}%)")
                
        except Exception as e:
            print(f"⚠️ Error en comité para {empresa}: {e}")

    elite_picks = sorted(candidatos, key=lambda x: x['fiabilidad'], reverse=True)[:5]
    
    if not elite_picks:
        msg_proteccion = f"📡 *Escaneo V10.2:* Cero señales >54%. Capital de ${saldo_actual:.2f} protegido. 🛡️"
        print(f"\n{msg_proteccion}")
        notifier.enviar_telegram(msg_proteccion)
    else:
        print(f"\n🎯 DISPARANDO {len(elite_picks)} ORDENES AL BROKER...")
        for pick in elite_picks:
            fiab = pick['fiabilidad']
            prob_dec = pick['prob_decimal']
            ticker = pick['ticker']
            precio = pick['precio']
            
            porcentaje_kelly = calcular_kelly(prob_dec)
            monto = saldo_actual * porcentaje_kelly
            
            resultado_orden = broker_api.ejecutar_orden_mercado(ticker, monto, precio)
            
            if resultado_orden == "ORDEN_COMPLETADA":
                prefijo = "⚡ *ORDEN EJECUTADA EN ALPACA*"
                logger_engine.guardar_registro(ticker, precio, pick['señal'], fiab, monto)
            else:
                prefijo = "❌ *ERROR DE EJECUCIÓN*"

            msg = (f"{prefijo}\n"
                   f"📊 Activo: {ticker}\n"
                   f"🧠 Confianza Cuádruple: {fiab}%\n"
                   f"💰 Inversión Asignada: ${monto:.2f}\n"
                   f"⚖️ Riesgo Kelly: {(porcentaje_kelly*100):.2f}%")
            
            notifier.enviar_telegram(msg)
        
    try:
        report_generator.generar_y_enviar_reporte()
    except Exception as e:
        print(f"⚠️ Error en reporte: {e}")
        
    print("-" * 50)
    print("🛑 PROTOCOLO V10.2 FINALIZADO.")

if __name__ == "__main__":
    ejecutar_analisis_dinamico()