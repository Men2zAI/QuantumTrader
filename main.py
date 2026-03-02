import brain
import notifier
import logger_engine
import validator
import json
import os

# Tu lista base de 20 sensores
EMPRESAS = [
    "NVDA", "AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "META", "NFLX", 
    "AMD", "INTC", "PYPL", "ADBE", "CSCO", "PEP", "COST", "AVGO", 
    "QCOM", "TMUS", "TXN", "AMAT"
]

def ejecutar_analisis():
    # 1. Auditoría del pasado
    print("⚖️ Auditando resultados...")
    validator.validar_predicciones()
    
    # 2. Cargar quién tiene permiso para invertir hoy
    elegidos = []
    if os.path.exists('elegidos.json'):
        with open('elegidos.json', 'r') as f:
            elegidos = json.load(f)
    else:
        # Si es la primera vez, todos empiezan con oportunidad
        elegidos = EMPRESAS

    print(f"🚀 Iniciando escaneo selectivo...")
    
    for empresa in EMPRESAS:
        try:
            df = brain.obtener_datos(empresa)
            señal, precio, fiabilidad = brain.predecir(df, empresa)
            
            # SIEMPRE guardamos el registro para que el analizador aprenda
            logger_engine.guardar_registro(empresa, precio, señal, fiabilidad)
            
            # FILTRO DE INVERSIÓN: Solo si es rentable y tiene alta confianza
            if empresa in elegidos and "ALTA CONFIANZA" in señal and fiabilidad >= 55.0:
                msg = f"💰 *OPERACIÓN ACTIVA:* {empresa}\n📍 Precio: ${precio}\n🎯 Fiabilidad: {fiabilidad}%"
                notifier.enviar_telegram(msg)
                print(f"🔥 Señal activa para {empresa}")
            else:
                print(f"👁️ Monitorización pasiva de {empresa}...")

        except Exception as e:
            print(f"❌ Error en {empresa}: {e}")

if __name__ == "__main__":
    ejecutar_analisis()