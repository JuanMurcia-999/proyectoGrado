import requests


def Get_features_agent(Ip):

    URL = f'http://localhost:8000/agents/features/agent/{Ip}'

    response = requests.get(URL)
    # Verificar que la petición fue exitosa (código de estado 200)
    if response.status_code == 200:
        # Convertir la respuesta JSON a un diccionario de Python
        data = response.json()
        # Devolver el resultado
        print(data)
        return data
    else:
        return f"Error en la petición: {response.status_code}"
Get_features_agent('192.168.20.27')