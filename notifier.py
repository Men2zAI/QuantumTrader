import requests
import os

def enviar_telegram(mensaje):
    """
    Envía un reporte de trading al chat de Telegram configurado.
    """
    # GitHub Actions inyecta estos valores desde los Secrets
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("❌ Error: TELEGRAM_TOKEN o TELEGRAM_CHAT_ID no detectados en el entorno.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': mensaje,
        'parse_mode': 'Markdown' # Para que las negritas y emojis se vean bien
    }
    
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ Notificación enviada con éxito.")
        else:
            print(f"⚠️ Telegram respondió con error: {response.text}")
    except Exception as e:
        print(f"❌ Fallo en la conexión de red con Telegram: {e}")
        
def enviar_imagen_telegram(ruta_imagen, mensaje=""):
    # Por ahora, solo enviamos el texto para evitar que el bot se estrelle
    # En el futuro aquí pondremos el código real para enviar fotos
    enviar_telegram(f"📊 [Gráfico Generado]: {mensaje}")
    print(f"Simulando envío de imagen: {ruta_imagen}")