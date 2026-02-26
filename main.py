import brain
import notifier
import logger_engine
import validator

# Lista expandida para mayor robustez estadística
EMPRESAS = [
    "NVDA", "AAPL", "MSFT", "TSLA", "GOOGL", # Tus originales
    "AMZN", "META", "NFLX", "AMD", "INTC",   # Big Tech
    "PYPL", "ADBE", "CSCO", "PEP", "COST",   # Consumo y Redes
    "AVGO", "QCOM", "TMUS", "TXN", "AMAT"    # Semiconductores y Telecom
]

def ejecutar_analisis():
    # 1. Fase de Auditoría
    print(f"⚖️ Auditando {len(EMPRESAS)} activos...")
    validator.validar_predicciones()
    
    # 2. Fase de Escaneo
    print(f"🚀 Iniciando escaneo de {len(EMPRESAS)} señales de mercado...")
    
    for empresa in EMPRESAS:
        try:
            df = brain.obtener_datos(empresa)
            señal, precio, fiabilidad = brain.predecir(df, empresa)
            
            # Registrar en el CSV
            logger_engine.guardar_registro(empresa, precio, señal, fiabilidad)
            
            # Solo notificar por Telegram señales de ALTA CONFIANZA
            # Evitamos saturar el móvil con 20 mensajes
            if "ALTA CONFIANZA" in señal:
                mensaje = f"🔥 *ALTA CONFIANZA:* {empresa}\n📍 Precio: ${precio}\n📊 RSI/VOL Confirmado\n🎯 Fiabilidad: {fiabilidad}%"
                notifier.enviar_telegram(mensaje)
                print(f"📢 Señal fuerte enviada para {empresa}")
                
        except Exception as e:
            print(f"❌ Error en sensor {empresa}: {e}")

if __name__ == "__main__":
    ejecutar_analisis()