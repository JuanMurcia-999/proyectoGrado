import schemas
import crud

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
            state =await crud.add_history(schemas.addHistory(**data))
        file.truncate(0)
