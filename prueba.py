import psutil

def memoria_ram_usada():
    # Obtiene la información de la memoria
    memoria = psutil.virtual_memory()

    # Muestra la memoria total, la utilizada y la disponible
    print(f"Memoria total: {memoria.total / (1024 ** 2):.2f} MB")
    print(f"Memoria utilizada: {round(memoria.used / (1024 ** 2))} MB")
    print(f"Memoria disponible: {memoria.available / (1024 ** 2):.2f} MB")
    print(f"Porcentaje de memoria utilizada: {memoria.percent}%")

# Llama a la función
memoria_ram_usada()
