from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
from slim.slim_get import slim_get
import asyncio
from DataBases import schemas
import subprocess



async def ping(ip: str):

    p = subprocess.Popen(
        ["ping", "-n", "2", "-w", "2", ip],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    p.wait()
    return True if p.poll() == 0 else False


async def peticion(community, ip, port, objects):
    return await slim_get(
        community,
        ip,
        port,     
        *objects
    )


class AnchoBanda:

    ifInOctets = "1.3.6.1.2.1.2.2.1.10"
    ifOutOctets = "1.3.6.1.2.1.2.2.1.16"

    def __init__(self, Config: schemas.ConfigAnchoBanda) -> None:
        self.ip = Config.ip
        self.Num_Interface = Config.Num_Interface
        self.intervalo = Config.intervalo 
        self.id_adminis = Config.id_adminis
        self.id = Config.id
        self.cola = Config.history
        self.alarms = Config.alarms

    async def run(self):
        print(f"Ejecutando run de {self.ip}")
        while True:
            try:
                community = "public"
                port = 161
                InOut1 = []
                InOut2 = []
                objects = [
                    ObjectType(ObjectIdentity(self.ifInOctets + "." + self.Num_Interface)),
                    ObjectType(ObjectIdentity(self.ifOutOctets + "." + self.Num_Interface))
                ]

                varbinds = await peticion(community, self.ip, port,objects)

                for varBind in varbinds:
                    _, value = varBind
                    InOut1.append(int(value))

                await asyncio.sleep(self.intervalo)

                varbinds = await peticion(community, self.ip, port, objects)

                for varBind in varbinds:
                    _, value = varBind
                    InOut2.append(int(value))
                    
                # procesamiento de la lectura
                [difIn, difOut] = InOut2[0] - InOut1[0], InOut2[1] - InOut1[1]
                [difInbits, difOutbits] = difIn * 8, difOut * 8
                in_bps = difInbits / self.intervalo
                out_bps = difOutbits / self.intervalo

                [in_kbps, out_kbps] = in_bps / 1000, out_bps / 1000

                dIn = {
                    "id_agent": self.id,
                    "id_adminis": int("100" + self.Num_Interface + "0"),
                    "value": round(in_kbps, 3),
                }

                dOut = {
                    "id_agent": self.id,
                    "id_adminis": int("100" + self.Num_Interface + "1"),
                    "value": round(out_kbps, 3),
                }

                record1 = schemas.addHistory(**dIn)
                record2 = schemas.addHistory(**dOut)



                self.cola.encolar(record1)
                self.cola.encolar(record2)
                self.alarms.encolar(record1)
                self.alarms.encolar(record2)

            except asyncio.CancelledError:
                print(f"Task was cancelled")
                break


class Processes:
    def __init__(self, Config: schemas.ConfigProcesses) -> None:
        self.ip = Config.ip
        self.timer = Config.timer | 60
        self.id_adminis = Config.id_adminis
        self.id = Config.id
        self.cola = Config.history
        self.alarms = Config.alarms

    async def TaskNumProcesses(self):
        while True:
            try:
                community="public"
                port=161
                objects= [ObjectType(ObjectIdentity("1.3.6.1.2.1.25.1.6.0"))]
                varbinds = await peticion(community, self.ip, port, objects)
                _, num_processes = varbinds[0]
                num_processes = int(num_processes)

                print(f"Numero de procesos {num_processes} ::::  {self.id_adminis}")
                datos = {
                    "id_agent": self.id,
                    "id_adminis": self.id_adminis,
                    "value": num_processes,
                }

                record = schemas.addHistory(**datos)
                self.cola.encolar(record)
                self.alarms.encolar(record)

                await asyncio.sleep(self.timer)
            except asyncio.CancelledError:
                print(f"Task was cancelled")
                break

    async def TaskMemorySize(self):
        while True:
            try:
                community="public"
                port=161
                objects=[ObjectType(ObjectIdentity("1.3.6.1.2.1.25.2.2.0"))]
                varbinds = await peticion(community, self.ip, port, objects)


                _, MemorySize = varbinds[0]
                MemorySize = int(MemorySize)

                print(f"Memoria total {MemorySize}")
                datos = {
                    "id_agent": self.id,
                    "id_adminis": self.id_adminis,
                    "value": MemorySize,
                }

                record = schemas.addHistory(**datos)
                self.cola.encolar(record)
                self.alarms.encolar(record)

                await asyncio.sleep(self.timer)
            except asyncio.CancelledError:
                print(f"Task was cancelled")
                break
