import requests


TOKEN = "7185760712:AAGz1-hK22zzC8X9r8KKtqjBxVOx1NSVCR4"
CHAT_ID = "-1002147532737"

mensaje='Funcione perro'

def sendmessage(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje}
    response = requests.post(url, data=payload)
    return response.json()



