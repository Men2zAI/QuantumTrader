import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("TELEGRAM_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

def diagnostico():
    print("--- INICIANDO DIAGNÓSTICO ---")
    
    # Verificamos si las variables cargaron
    if not token:
        print("❌ ERROR: No se encontró el TELEGRAM_TOKEN en el archivo .env")
        return
    if not chat_id:
        print("❌ ERROR: No se encontró el TELEGRAM_CHAT_ID en el archivo .env")
        return
        
    print(f"📡 Intentando conectar con Token: {token[:10]}...")
    print(f"👤 Destinatario ID: {chat_id}")
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": "Probando conexión robusta... 🦾"}
    
    try:
        r = requests.post(url, data=payload)
        print(f"Status Code: {r.status_code}")
        print(f"Respuesta del servidor: {r.text}")
        
        if r.status_code == 200:
            print("✅ ¡MENSAJE ENVIADO! Revisa tu Telegram.")
        elif r.status_code == 401:
            print("❌ ERROR 401: El Token es inválido. Revísalo bien.")
        elif r.status_code == 400:
            print("❌ ERROR 400: El Chat ID es incorrecto o no has iniciado el bot.")
    except Exception as e:
        print(f"❌ ERROR DE RED: {e}")

if __name__ == "__main__":
    diagnostico()