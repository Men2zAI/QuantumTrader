import brain
import notifier
import logger_engine
import validator
import json
import os
import pandas as pd

EMPRESAS = ["NVDA", "AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "META", "NFLX", 
            "AMD", "INTC", "PYPL", "ADBE", "CSCO", "PEP", "COST", "AVGO", 
            "QCOM", "TMUS", "TXN", "AMAT"]

def ejecutar_analisis_dinamico():
    # 1. Auditoría: Revisar si los sensores tocaron Stop Loss o Take Profit
    validator.validar_predicciones()
    
    # 2. Leer el capital disponible (Interés Compuesto)
    with open('wallet.json', 'r') as f:
        saldo_actual = json.load(f)['saldo_total']
        
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
    for empresa in EMPRESAS:
        # Si la empresa ya está operando, el sensor la ignora para no sobre-comprar
        if empresa in acciones_abiertas:
            continue
            
        try:
            df = brain.obtener_datos(empresa)
            señal, precio, fiabilidad = brain.predecir(df, empresa)
            
            # Filtro base (>52%)
            if empresa in elegidos and "ALTA CONFIANZA" in señal and fiabilidad >= 52.0:
                candidatos.append({
                    'ticker': empresa,
                    'precio': precio,
                    'señal': señal,
                    'fiabilidad': fiabilidad
                })
        except Exception as e:
            print(f"⚠️ Error en sensor {empresa}: {e}")

    # 4. SELECCIÓN TOP 5
    elite_picks = sorted(candidatos, key=lambda x: x['fiabilidad'], reverse=True)[:5]
    
    # 5. GESTIÓN DE CAPITAL (INTERÉS COMPUESTO)
    if not elite_picks:
        notifier.enviar_telegram(f"📡 *Escaneo:* No hay nuevas señales claras (>52%). Capital de ${saldo_actual:.2f} protegido. 🛡️")
    else:
        for pick in elite_picks:
            fiab = pick['fiabilidad']
            
            # Cálculo de inversión por porcentajes del saldo total
            if fiab >= 60.0:
                monto = saldo_actual * 0.20
                prefijo = "🚀 *ÉLITE CONVICCIÓN*"
            elif fiab >= 55.0:
                monto = saldo_actual * 0.10
                prefijo = "🎯 *ÉLITE ESTÁNDAR*"
            else:
                monto = saldo_actual * 0.05
                prefijo = "🔬 *ÉLITE EXPLORACIÓN*"

            # Guardamos el registro con el monto calculado dinámicamente
            logger_engine.guardar_registro(pick['ticker'], pick['precio'], pick['señal'], fiab, monto)

            msg = (f"{prefijo}: {pick['ticker']}\n"
                   f"📍 Precio: ${pick['precio']:.2f}\n"
                   f"📊 Fiabilidad: {fiab}%\n"
                   f"💰 Inversión: ${monto:.2f} ({(monto/saldo_actual)*100:.0f}%)")
            
            notifier.enviar_telegram(msg)
        
        notifier.enviar_telegram(f"✅ Escaneo finalizado con {len(elite_picks)} nuevas señales dinámicas.")

if __name__ == "__main__":
    ejecutar_analisis_dinamico()