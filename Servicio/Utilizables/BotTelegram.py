import requests
from settings import Settings

settings = Settings()

def sendmessage(mensaje):
    url = f"https://api.telegram.org/bot{settings.TOKENTELEGRAM}/sendMessage"
    payload = {"chat_id": settings.CHAT_ID, "text": mensaje}
    response = requests.post(url, data=payload)
    return response.json()
