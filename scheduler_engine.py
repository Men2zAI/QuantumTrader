from apscheduler.schedulers.blocking import BlockingScheduler
from main import run_quantum_system
from notifier import TelegramNotifier
import logging

# Configuración de credenciales (Cámbialas por las tuyas)
TELEGRAM_TOKEN = "TU_TOKEN_AQUÍ"
CHAT_ID = "TU_CHAT_ID_AQUÍ"

notifier = TelegramNotifier(TELEGRAM_TOKEN, CHAT_ID)
scheduler = BlockingScheduler()

def scheduled_job():
    ticker = "NVDA"
    try:
        # Ejecutamos el sistema
        run_quantum_system(ticker)
        
        # Opcional: Podrías modificar run_quantum_system para que devuelva un resumen
        # y enviarlo por notifier.send_notification(resumen)
        
    except Exception as e:
        notifier.send_notification(f"⚠️ <b>ALERTA DE SISTEMA</b>\nFallo en la ejecución programada: {str(e)}")

# Programación: De lunes a viernes a las 10:00 AM (cuando abre el mercado)
scheduler.add_job(scheduled_job, 'cron', day_of_week='mon-fri', hour=10, minute=0)

if __name__ == "__main__":
    print("🤖 Agente Autónomo activado. Esperando apertura del mercado...")
    notifier.send_notification("🚀 <b>Sistema QuantumTrader en línea</b>\nModo autónomo activado.")
    scheduler.start()