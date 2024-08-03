import psutil
import time

def get_network_stats(interval):
    net1 = psutil.net_io_counters()
    time.sleep(interval)
    net2 = psutil.net_io_counters()
    
    bytes_sent = net2.bytes_sent - net1.bytes_sent
    bytes_recv = net2.bytes_recv - net1.bytes_recv
    
    return bytes_sent, bytes_recv



async def UseCPU():
    pass



def main():
    interval = 5  # Intervalo de tiempo en segundos
    while True:
        bytes_sent, bytes_recv = get_network_stats(interval)
        sent_kbps = (bytes_sent * 8) / 1000  # Convertir a kilobits por segundo
        recv_kbps = (bytes_recv * 8) / 1000  # Convertir a kilobits por segundo
        
        print(f"Enviado: {sent_kbps:.2f} kbps, Recibido: {recv_kbps:.2f} kbps")
        time.sleep(interval)

if __name__ == "__main__":
    main()
