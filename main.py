import brain
import notifier
import logger_engine
import json
import os

def ejecutar_analisis_elite():
    EMPRESAS = ["NVDA", "AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "META", "NFLX", 
                "AMD", "INTC", "PYPL", "ADBE", "CSCO", "PEP", "COST", "AVGO", 
                "QCOM", "TMUS", "TXN", "AMAT"]
    
    # 1. Cargar "Elegidos" (los que históricamente dan dinero)
    elegidos = []
    if os.path.exists('elegidos.json'):
        with open('elegidos.json', 'r') as f:
            elegidos = json.load(f)

    candidatos = []

    # 2. Análisis de todas (para que el bot siga aprendiendo)
    for empresa in EMPRESAS:
        try:
            df = brain.obtener_datos(empresa)
            señal, precio, fiabilidad = brain.predecir(df, empresa)
            
            # Guardamos siempre el registro para el historial global
            logger_engine.guardar_registro(empresa, precio, señal, fiabilidad)
            
            # Solo consideramos para "Inversión de Élite" si es rentable y tiene alta confianza
            if empresa in elegidos and "ALTA CONFIANZA" in señal and fiabilidad >= 55.0:
                candidatos.append({
                    'ticker': empresa,
                    'precio': precio,
                    'señal': señal,
                    'fiabilidad': fiabilidad
                })
        except Exception as e:
            print(f"❌ Error en sensor {empresa}: {e}")

    # 3. SELECCIÓN DE ÉLITE: Ordenar por fiabilidad y tomar las TOP 3-5
    # Ordenamos de mayor a menor fiabilidad
    elite_picks = sorted(candidatos, key=lambda x: x['fiabilidad'], reverse=True)[:5]
    
    # 4. Notificar solo las elegidas para invertir
    for pick in elite_picks:
        msg = f"🎯 *OPERACIÓN DE ÉLITE:* {pick['ticker']}\n📍 Precio: ${pick['precio']}\n📊 Fiabilidad: {pick['fiabilidad']}%"
        notifier.enviar_telegram(msg)
    
    # Guardamos las picks de hoy para que el auditor sepa en qué invertimos realmente
    with open('operaciones_activas.json', 'w') as f:
        json.dump(elite_picks, f)

if __name__ == "__main__":
    ejecutar_analisis_elite()