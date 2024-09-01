import psutil

def get_memory_usage():
    # Obtener información de la memoria
    memory_info = psutil.virtual_memory()
    
    # Extraer la cantidad de memoria en uso
    used_memory = memory_info.used
    total_memory = memory_info.total
    used_memory_percent = memory_info.percent

    return used_memory, total_memory, used_memory_percent

if __name__ == "__main__":
    used, total, percent = get_memory_usage()
    print(f"Memoria en uso: {used / (1024 ** 2):.2f} MB")
    print(f"Memoria total: {total / (1024 ** 2):.2f} MB")
    print(f"Porcentaje de memoria en uso: {percent}%")
