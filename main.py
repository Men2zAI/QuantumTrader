import brain
import notifier
import logger_engine
import validator
import json
import os
import pandas as pd
import report_generator

EMPRESAS = ["NVDA", "AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "META", "NFLX", 
            "AMD", "INTC", "PYPL", "ADBE", "CSCO", "PEP", "COST", "AVGO", 
            "QCOM", "TMUS", "TXN", "AMAT"]

def ejecutar_analisis_dinamico():
    print("🚀 INICIANDO PROTOCOLO DE ORQUESTACIÓN Y AUDITORÍA...")
    
    # 1. Auditoría: Revisar si los sensores tocaron Stop Loss o Take Profit
    try:
        validator.validar_predicciones()
    except Exception as e:
        print(f"⚠️ Aviso en Auditoría: {e}")
    
    # 2. Leer el capital disponible (Interés Compuesto)
    try:
        with open('wallet.json', 'r') as f:
            saldo_actual = json.load(f)['saldo_total']
    except FileNotFoundError:
        print("⚠️ No se encontró wallet.json. Usando saldo base de $1000.00")
        saldo_actual = 1000.00
        
    elegidos = []
    if os.path.exists('elegidos.json'):
        with open('elegidos.json', 'r') as f:
            elegidos = json.load(f)
    else:
        elegidos = EMPRESAS

    # NUEVO CANDADO ANTI-DUPLICADOS: Leer operaciones activas
    acciones_abiertas = []
    if os.path.exists('historial_decisiones.csv'):
        df_hist = pd.read_csv('historial_decisiones.csv')
        abiertas_df = df_hist[df_hist['resultado_real'] == 'PENDIENTE']
        acciones_abiertas = abiertas_df['ticker'].tolist()

    candidatos = []
    
    # 3. Escaneo Global
    print("📡 Iniciando barrido de la red de sensores XGBoost...")
    for empresa in EMPRESAS:
        # Si la empresa ya está operando, el sensor la ignora para no sobre-comprar
        if empresa in acciones_abiertas:
            print(f"⏳ {empresa}: Omitida (Operación ya activa en el mercado).")
            continue
            
        try:
            df = brain.obtener_datos(empresa)
            señal, precio, fiabilidad = brain.predecir(df, empresa)
            
            # 🛡️ FILTRO INSTITUCIONAL: Exigimos 60% mínimo para evitar ruido
            if empresa in elegidos and "ALTA CONFIANZA" in señal and fiabilidad >= 60.0:
                candidatos.append({
                    'ticker': empresa,
                    'precio': precio,
                    'señal': señal,
                    'fiabilidad': fiabilidad
                })
                print(f"✅ {empresa}: ¡SEÑAL DETECTADA! ({fiabilidad}%)")
            else:
                print(f"   {empresa}: Descartada (Señal: {señal} - {fiabilidad}%)")
                
        except Exception as e:
            print(f"⚠️ Error en sensor {empresa}: {e}")

    # 4. SELECCIÓN TOP 5
    elite_picks = sorted(candidatos, key=lambda x: x['fiabilidad'], reverse=True)[:5]
    
    # 5. GESTIÓN DE CAPITAL (INTERÉS COMPUESTO)
    if not elite_picks:
        msg_proteccion = f"📡 *Escaneo:* No hay nuevas señales claras (>60%). Capital de ${saldo_actual:.2f} protegido. 🛡️"
        print(f"\n{msg_proteccion}")
        notifier.enviar_telegram(msg_proteccion)
    else:
        print(f"\n🎯 Procesando {len(elite_picks)} operaciones aprobadas...")
        for pick in elite_picks:
            fiab = pick['fiabilidad']
            
            # 🛡️ GESTIÓN DE RIESGO: Límite máximo del 10% por operación
            if fiab >= 65.0:
                monto = saldo_actual * 0.10
                prefijo = "🚀 *ÉLITE CONVICCIÓN*"
            elif fiab >= 62.0:
                monto = saldo_actual * 0.05
                prefijo = "🎯 *ÉLITE ESTÁNDAR*"
            else:
                monto = saldo_actual * 0.02
                prefijo = "🔬 *ÉLITE EXPLORACIÓN*"

            # Guardamos el registro con el monto calculado dinámicamente
            logger_engine.guardar_registro(pick['ticker'], pick['precio'], pick['señal'], fiab, monto)

            msg = (f"{prefijo}: {pick['ticker']}\n"
                   f"📍 Precio: ${pick['precio']:.2f}\n"
                   f"📊 Fiabilidad: {fiab}%\n"
                   f"💰 Inversión: ${monto:.2f} ({(monto/saldo_actual)*100:.0f}%)")
            
            notifier.enviar_telegram(msg)
        
        notifier.enviar_telegram(f"✅ Escaneo finalizado con {len(elite_picks)} nuevas señales dinámicas.")
    
    # Generar el reporte final de la cartera
    try:
        report_generator.generar_y_enviar_reporte()
        print("📄 Reporte generado y enviado con éxito.")
    except Exception as e:
        print(f"⚠️ Error generando reporte: {e}")
        
    print("-" * 50)
    print("🛑 PROTOCOLO FINALIZADO.")

if __name__ == "__main__":
    ejecutar_analisis_dinamico()