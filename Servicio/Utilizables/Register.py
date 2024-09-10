import aiofiles

def Writer(text):
    with open('archivo.txt', 'a') as archivo:
        archivo.write(text)