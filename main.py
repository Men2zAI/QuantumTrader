import brain
import notifier
import logger_engine
import validator
import json
import os

# Tu matriz de 20 sensores
EMPRESAS = ["NVDA", "AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "META", "NFLX", 
            "AMD", "INTC", "PYPL", "ADBE", "CSCO", "PEP", "COST", "AVGO", 
            "QCOM", "TMUS", "TXN", "AMAT"]

def ejecutar_analisis_elite():
    # 1. Auditoría: Cerramos el ciclo anterior y actualizamos el saldo
    print("⚖️ Ejecutando auditoría de operaciones previas...")
    validator.validar_predicciones()
    
    # 2. Carga de activos rentables (Elegidos)
    elegidos = []
    if os.path.exists('elegidos.json'):
        with open('elegidos.json', 'r') as f:
            elegidos = json.load(f)
    else:
        # Si el archivo no existe aún, todos tienen oportunidad
        elegidos = EMPRESAS

    candidatos = []
    print(f"🚀 Analizando {len(EMPRESAS)} activos en busca de oportunidades de Élite...")

    # 3. Bucle de análisis global
    for empresa in EMPRESAS:
        try:
            df = brain.obtener_datos(empresa)
            señal, precio, fiabilidad = brain.predecir(df, empresa)
            
            # SIEMPRE registramos para que el sistema siga aprendiendo
            logger_engine.guardar_registro(empresa, precio, señal, fiabilidad)
            
            # FILTRO DE ÉLITE: Debe ser rentable históricamente Y tener alta confianza > 55%
            if empresa in elegidos and "ALTA CONFIANZA" in señal and fiabilidad >= 55.0:
                candidatos.append({
                    'ticker': empresa,
                    'precio': precio,
                    'señal': señal,
                    'fiabilidad': fiabilidad
                })
                print(f"🎯 Candidato de Élite detectado: {empresa} ({fiabilidad}%)")
            else:
                print(f"👁️ {empresa} monitorizada (No cumple requisitos de Élite)")

        except Exception as e:
            print(f"❌ Error crítico en sensor {empresa}: {e}")

    # 4. SELECCIÓN TOP 5: Ordenamos por la fiabilidad más alta
    elite_picks = sorted(candidatos, key=lambda x: x['fiabilidad'], reverse=True)[:5]
    
    # 5. SISTEMA DE AVISO DE VIDA: Siempre enviamos algo a Telegram
    if not elite_picks:
        status_msg = "📡 *Escaneo Finalizado:* No se detectaron oportunidades de Élite con fiabilidad > 55%. Tu capital de $1,025.69 está a salvo. 🛡️"
        notifier.enviar_telegram(status_msg)
        print("🛡️ No hubo señales de alta probabilidad hoy.")
    else:
        for pick in elite_picks:
            msg = f"🎯 *OPERACIÓN DE ÉLITE:* {pick['ticker']}\n📍 Precio: ${pick['precio']:.2f}\n📊 Fiabilidad: {pick['fiabilidad']}%"
            notifier.enviar_telegram(msg)
        
        notifier.enviar_telegram(f"✅ *Escaneo Finalizado:* Se han detectado {len(elite_picks)} activos de Élite.")
        print(f"🔥 Se enviaron {len(elite_picks)} alertas a Telegram.")

if __name__ == "__main__":
    ejecutar_analisis_elite()