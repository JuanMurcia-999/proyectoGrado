from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
from slim.slim_get import slim_get
import asyncio

async def peticion(community, host, port, Num_Interface):
    ifInOctets = '1.3.6.1.2.1.2.2.1.10'
    ifOutOctets = '1.3.6.1.2.1.2.2.1.16'
    return await slim_get(
        community, host, port,
        ObjectType(ObjectIdentity(ifInOctets + '.' + Num_Interface)),
        ObjectType(ObjectIdentity(ifOutOctets + '.' + Num_Interface))
    )

class AnchoBanda:
    def __init__(self, host: str, Num_Interface: str, intervalo: int) -> None:
        self.host = host
        self.Num_Interface = Num_Interface
        self.intervalo = intervalo

    async def run(self):
        print(f'Ejecutando run de {self.host}')
        while True:
            community = 'public'
            port = 161
            InOut1 = []
            InOut2 = []

            varbinds = await peticion(community, self.host, port, self.Num_Interface)
            for varBind in varbinds:
                _, value = varBind
                InOut1.append(int(value))

            await asyncio.sleep(self.intervalo)

            varbinds = await peticion(community, self.host, port, self.Num_Interface)
            for varBind in varbinds:
                _, value = varBind
                InOut2.append(int(value))

            [difIn, difOut] = InOut2[0] - InOut1[0], InOut2[1] - InOut1[1]
            [difInbits, difOutbits] = difIn * 8, difOut * 8
            in_bps = difInbits / self.intervalo
            out_bps = difOutbits / self.intervalo

            [in_kbps, out_kbps] = in_bps / 1000, out_bps / 1000

            print(f'Kbps IN: {in_kbps} /// Kbps OUT {out_kbps}')



class Memorysize:
    def __init__(self, ip:str,timer:int) -> None:
        self.ip=ip
        self.timer=timer
    
    async def run(self):
        await slim_get(
        'public',self.ip, 161,
        ObjectType(ObjectIdentity('1.3.6.1.2.1.25.2.2.0')),
    )
        


class Processes:
    def __init__(self, ip:str,timer:int) -> None:
        self.ip=ip
        self.timer=timer|10
    
    async def TaskNumProcesses(self):
        while True:
            
            varbinds = await slim_get(
            'public', self.ip, 161,
            ObjectType(ObjectIdentity('1.3.6.1.2.1.25.1.6.0'))
        )
            _, num_processes = varbinds[0]
            num_processes=int(num_processes)

            print(f'Numero de procesos {num_processes}')    
            await asyncio.sleep(self.timer)
    

    async def TaskMemorySize(self):
        while True:
            varbinds= await slim_get(
                'public',self.ip, 161,
                ObjectType(ObjectIdentity('1.3.6.1.2.1.25.2.2.0')),)

            _, MemorySize = varbinds[0]
            MemorySize=int(MemorySize)

            print(f'Memoria total {MemorySize}')    
            await asyncio.sleep(self.timer)