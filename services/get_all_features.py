import requests

URL = 'http://localhost:8000/agents/features/all/'


def Get_all_features():


    response = requests.get(URL)
    # Verificar que la petición fue exitosa (código de estado 200)
    if response.status_code == 200:
        # Convertir la respuesta JSON a un diccionario de Python
        data = response.json()
        # Devolver el resultado
        return data
    else:
        return f"Error en la petición: {response.status_code}"
