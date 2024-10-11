# from schema.history_schemas import addHistory

from ..services.queue_services import add_history
from ..schema.history_schemas import addHistory

def Writer(text):
    with open('archivo.txt', 'a') as archivo:
        archivo.write(text)

def Buffer(text):
    with open('buffer.txt', 'a') as archivo:
        archivo.write(text)

async def Read():
    with open('buffer.txt',"r+") as file:
        for line in file:
            parts = line.strip().split()
            data = {key: value.strip("'") for key, value in (part.split('=', 1) for part in parts)}
            print(data)
            state =await add_history(addHistory(**data))
        file.truncate(0)
