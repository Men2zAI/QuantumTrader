import brain
import notifier
import logger_engine
import validator # <--- Importamos el nuevo validador

EMPRESAS = ["NVDA", "AAPL", "MSFT", "TSLA", "GOOGL"]

def ejecutar_analisis():
    # 1. Primero auditamos el pasado
    print("⚖️ Auditando predicciones anteriores...")
    validator.validar_predicciones()
    
    print("🚀 Iniciando escaneo de mercado actual...")
        
    for ticker in EMPRESAS:
        try:
            # 1. Obtener datos y predicción
            datos = brain.obtener_datos(ticker)
            señal, precio, fiabilidad = brain.predecir(df, empresa)
            
            # 2. Registrar en el historial (CSV)
            logger_engine.registrar_decision(ticker, precio_actual, señal, fiabilidad)
            
            # 3. Notificar a Telegram
            mensaje = (f"📊 *Reporte: {ticker}*\n"
                       f"💰 Precio: ${precio_actual}\n"
                       f"🧠 Señal: {señal}\n"
                       f"🎯 Fiabilidad: {fiabilidad}%")
            notifier.enviar_telegram(mensaje)
            
        except Exception as e:
            print(f"❌ Error analizando {ticker}: {e}")

if __name__ == "__main__":
    ejecutar_analisis()