<<<<<<< HEAD
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class TelegramNotifier:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_notification(self, message):
        if not self.token or not self.chat_id:
            print("❌ Error: Faltan credenciales en el .env")
            return
            
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(self.url, data=payload)
            return response.json()
        except Exception as e:
=======
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class TelegramNotifier:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_notification(self, message):
        if not self.token or not self.chat_id:
            print("❌ Error: Faltan credenciales en el .env")
            return
            
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(self.url, data=payload)
            return response.json()
        except Exception as e:
>>>>>>> f166bfe0cf293ddad91f7123819bf678ce1e708d
            print(f"❌ Error de red en Notifier: {e}")