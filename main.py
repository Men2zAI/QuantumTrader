import brain
import notifier
import logger_engine

# Tu lista de vigilancia (puedes añadir las que quieras)
EMPRESAS = ["NVDA", "AAPL", "MSFT", "TSLA", "GOOGL"]

def ejecutar_analisis():
    print("🚀 Iniciando escaneo de mercado...")
    
    for ticker in EMPRESAS:
        try:
            # 1. Obtener datos y predicción
            datos = brain.obtener_datos(ticker)
            señal, precio_actual, fiabilidad = brain.predecir(datos)
            
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