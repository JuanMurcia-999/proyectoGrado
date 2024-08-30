from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
from slim.slim_get import slim_get
import asyncio
from DataBases import schemas
import subprocess
import time


class Ping:
    agentes = {}
    states = {}

    async def Exectping(self):
        while True:
            tasks = []

            for id, ip in self.agentes.items():
                tasks.append(self.ping_and_update_state(id, ip))
            # Ejecutar todas las tareas concurrentemente
            await asyncio.gather(*tasks)
            await asyncio.sleep(1.5)

    async def ping_and_update_state(self, id, ip):
        """Realiza el ping y actualiza el estado de forma concurrente"""
        state = await asyncio.to_thread(self.ping_host, ip)
        self.states[id] = state
        # print(self.states)

    def ping_host(self, ip):
        """Función bloqueante para ejecutar el ping"""
        p = subprocess.Popen(
            ["ping", "-n", "2", "-w", "2", ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        p.wait()
        return p.poll() == 0

    async def addagent(self, id, ip):
        self.agentes[id] = ip
        self.states[id] = True
        print(self.agentes)

    async def getstate(self, id):
        return self.states.get(id)

    async def deleteagent(self, id):
        self.agentes.pop(id)
        self.states.pop(id)


async def peticion(community, ip, port, objects):
    return await slim_get(community, ip, port, *objects)


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
                if await Ping().getstate(self.id):
                    community = "public"
                    port = 161
                    InOut1 = []
                    InOut2 = []
                    objects = [
                        ObjectType(
                            ObjectIdentity(self.ifInOctets + "." + self.Num_Interface)
                        ),
                        ObjectType(
                            ObjectIdentity(self.ifOutOctets + "." + self.Num_Interface)
                        ),
                    ]

                    varbinds = await peticion(community, self.ip, port, objects)
                    if varbinds:
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
                        print('Interfaces')
                        self.cola.encolar(record1)
                        self.cola.encolar(record2)
                        self.alarms.encolar(record1)
                        self.alarms.encolar(record2)

            except asyncio.CancelledError:
                return
            finally:
                try:
                    await asyncio.sleep(1)
                except asyncio.CancelledError:
                    break



class Processes:
    def __init__(self, Config: schemas.ConfigProcesses) -> None:
        self.ip = Config.ip
        self.timer = Config.timer | 20
        self.id_adminis = Config.id_adminis
        self.id = Config.id
        self.cola = Config.history
        self.alarms = Config.alarms
        self.forhistory = {}

    async def TaskNumProcesses(self):
        while True:
            await Ping().getstate(self.id)
            try:
                if await Ping().getstate(self.id):
                    community = "public"
                    port = 161
                    objects = [ObjectType(ObjectIdentity("1.3.6.1.2.1.25.1.6.0"))]
                    varbinds = await peticion(community, self.ip, port, objects)
                    if varbinds:
                        _, num_processes = varbinds[0]
                        num_processes = int(num_processes)

                        # print(f"Numero de procesos {num_processes} ::::  {self.id_adminis}")
                        datos = {
                            "id_agent": self.id,
                            "id_adminis": self.id_adminis,
                            "value": num_processes,
                        }

                        record = schemas.addHistory(**datos)
                        self.cola.encolar(record)
                        self.alarms.encolar(record)
            except asyncio.CancelledError:
                break
            finally:
                try:
                    await asyncio.sleep(self.timer)
                except asyncio.CancelledError:
                    break

    async def TaskMemorySize(self):
        while True:
            try:
                if await Ping().getstate(self.id):
                    community = "public"
                    port = 161
                    objects = [ObjectType(ObjectIdentity("1.3.6.1.2.1.25.2.2.0"))]
                    varbinds = await peticion(community, self.ip, port, objects)
                    if varbinds:
                        _, MemorySize = varbinds[0]
                        MemorySize = int(MemorySize)

                        # print(f"Memoria total {MemorySize}")
                        datos = {
                            "id_agent": self.id,
                            "id_adminis": self.id_adminis,
                            "value": MemorySize,
                        }
                        # print('MemorySize')
                        record = schemas.addHistory(**datos)
                        self.cola.encolar(record)
                        self.alarms.encolar(record)

            except asyncio.CancelledError:
                break
            finally:
                try:
                    await asyncio.sleep(self.timer)
                except asyncio.CancelledError:
                    break

    async def TaskMemoryUsed(self):
        while True:
            try:
                if await Ping().getstate(self.id):
                    community = "public"
                    port = 165
                    objects = [ObjectType(ObjectIdentity("1.3.6.1.3.100.4.0"))]
                    varbinds = await peticion(community, self.ip, port, objects)
                    if varbinds:
                        _, MemorySize = varbinds[0]
                        MemorySize = int(MemorySize)

                        # print(f"Memoria total {MemorySize}")
                        datos = {
                            "id_agent": self.id,
                            "id_adminis": self.id_adminis,
                            "value": MemorySize,
                        }
                        # print('MemoryUsed')
                        record = schemas.addHistory(**datos)
                        self.cola.encolar(record)
                        self.alarms.encolar(record)

            except asyncio.CancelledError:
                break
            finally:
                try:
                    await asyncio.sleep(self.timer)
                except asyncio.CancelledError:
                    break

    async def TaskDiskUsed(self):
        while True:
            try:
                if await Ping().getstate(self.id):
                    community = "public"
                    port = 165
                    objects = [
                        ObjectType(ObjectIdentity("1.3.6.1.3.100.6.2.2.2")),
                    ]

                    varbinds = await peticion(community, self.ip, port, objects)
                    if varbinds:
                        _, value = varbinds[0]
                        datos = {
                            "id_agent": self.id,
                            "id_adminis": self.id_adminis,
                            "value": int(value),
                        }
                        record = schemas.addHistory(**datos)
                        self.cola.encolar(record)
                        self.alarms.encolar(record)

            except asyncio.CancelledError:
                break
            finally:
                try:
                    await asyncio.sleep(self.timer)
                except asyncio.CancelledError:
                    break
    async def TaskCpuUsed(self):

        while True:
            try:
                if await Ping().getstate(self.id):
                    A = await peticion(
                        "public",
                        self.ip,
                        165,
                        [ObjectType(ObjectIdentity("1.3.6.1.3.100.5.2.0"))],
                    )
                    if A:
                        # print('CpuUsed')
                        _, NumCores = A[0]
                        self.forhistory["TaskCpuUsed"] = [
                            int(f"{self.id_adminis}{self.id}{i}")
                            for i in range(0, NumCores + 1)
                        ]
                        community = "public"
                        port = 165
                        A = await peticion(
                            community,
                            self.ip,
                            port,
                            [ObjectType(ObjectIdentity("1.3.6.1.3.100.5.2.0"))],
                        )
                        B = await peticion(
                            community,
                            self.ip,
                            port,
                            [ObjectType(ObjectIdentity("1.3.6.1.3.100.5.1.0"))],
                        )

                        _, CpuUsed = B[0]
                        datos = {
                            "id_agent": self.id,
                            "id_adminis": int(f"{self.id_adminis}{self.id}0"),
                            "value": int(CpuUsed),
                        }

                        record = schemas.addHistory(**datos)

                        self.cola.encolar(record)
                        record.id_adminis = 105
                        self.alarms.encolar(record)

                        oids = [
                            ObjectType(ObjectIdentity(f"1.3.6.1.3.100.5.2.2.{i}"))
                            for i in range(1, NumCores + 1)
                        ]
                        B = await peticion(community, self.ip, port, oids)

                        for varBind, name in zip(B, self.forhistory["TaskCpuUsed"][1:]):
                            _, CoreUsed = varBind
                            datos = {
                                "id_agent": self.id,
                                "id_adminis": name,
                                "value": int(CoreUsed),
                            }

                            record = schemas.addHistory(**datos)
                            self.cola.encolar(record)
            except asyncio.CancelledError:
                self.forhistory.clear()
                break
            finally:
                try:
                    await asyncio.sleep(self.timer)
                except asyncio.CancelledError:
                    break

