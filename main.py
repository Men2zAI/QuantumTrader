import brain
import notifier
import logger_engine
import validator

EMPRESAS = ["NVDA", "AAPL", "MSFT", "TSLA", "GOOGL"]

def ejecutar_analisis():
    # 1. Fase de Auditoría: Comprobar qué pasó con las señales de ayer
    print("⚖️ Auditando predicciones anteriores...")
    validator.validar_predicciones()
    
    # 2. Fase de Escaneo: Analizar el mercado actual
    print("🚀 Iniciando escaneo de mercado actual...")
    
    for empresa in EMPRESAS:
        try:
            # --- LA LÍNEA QUE FALTABA ---
            # Primero descargamos los datos para que 'df' exista
            df = brain.obtener_datos(empresa)
            
            # Ahora pasamos 'df' y el nombre de la empresa al cerebro
            señal, precio, fiabilidad = brain.predecir(df, empresa)
            
            # 3. Registrar en el CSV
            logger_engine.guardar_registro(empresa, precio, señal, fiabilidad)
            print(f"✅ Registro guardado para {empresa}")
            
            # 4. Notificar por Telegram (solo si no es NEUTRAL)
            if "NEUTRAL" not in señal:
                mensaje = f"🤖 *QuantumTrader:* {empresa}\n📍 Precio: ${precio}\n📊 Señal: {señal}\n🎯 Fiabilidad: {fiabilidad}%"
                notifier.enviar_telegram(mensaje)
                
        except Exception as e:
            print(f"❌ Error analizando {empresa}: {e}")

if __name__ == "__main__":
    ejecutar_analisis()