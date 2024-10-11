from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
from .Historyqueue import HistoryFIFOQueue
from .Alarmqueue import AlarmFIFOQueue
from .Utils.Gestionables import Ping
from .Utils.Register import Writer
from .slim.slim_get import slim_get
from .services import taskoid_services as crud
from .schema import taskoid_schemas as schema
from .schema.history_schemas import addHistory
import asyncio




history = HistoryFIFOQueue()
alarm = AlarmFIFOQueue()


async def Totalagentes(id_agent: int, ip_agent: str):
    try:
        TIMES = []
        OIDS = []
        IDF = []

        intervalos = await crud.get_unique_times(id_agent)
        # print(intervalos)
        for inter in intervalos:
            TIMES.append(inter)
            features = await crud.get_features_oid(inter, id_agent)

            OIDS.append([item.oid for item in features])
            IDF.append([item.id_adminis for item in features])

        return schema.elements(
            **{"ID": id_agent, "IP": ip_agent, "TIMES": TIMES, "OIDS": OIDS, "IDF": IDF}
        )
    except Exception:
        print("aglo paso en TotalAgentes")


async def Get_SNMP(task: schema.taskoid):
    numgets = 0
    while True:
        try:
            state = await Ping().getstate(task.ID)
            if state:
                varbinds = await slim_get("public", task.IP, 161, *task.OIDS)
                if varbinds:
                    numgets += 1
                    for cosa, id in zip(varbinds, task.IDF):
                        _, value = cosa

                        datos = {
                            "id_agent": task.ID,
                            "id_adminis": id,
                            "value": round(float(value), 3),
                        }

                        data = addHistory(**datos)
                        await history.add(data)
                        await alarm.add(data)

        except (asyncio.CancelledError, KeyboardInterrupt):
            print("fallo en OID")
            break
        finally:
            try:
                await asyncio.sleep(task.TIME*60)
            except (asyncio.CancelledError, KeyboardInterrupt):
                Writer(f"id_agent= {task.ID}, id_adminis= {id}, Ejecuciones= {numgets*len(task.OIDS)} Timer = {task.TIME}\n")
                break


class sensorOID:
    def __init__(self, ip: str, id: int) -> None:
        self.ip = ip
        self.id = id
        self.tasks = []

    async def CreatorTask(self):
        for task in self.tasks:
            task.cancel()
        elements = await Totalagentes(self.id, self.ip)
        # print(elements)
        for TIME, OIDS, IDF in zip(elements.TIMES, elements.OIDS, elements.IDF):
            oid = [ObjectType(ObjectIdentity(f"{oid}")) for oid in OIDS]
            self.tasks.append(
                asyncio.create_task(
                    Get_SNMP(
                        schema.taskoid(
                            **{
                                "TIME": TIME,
                                "OIDS": oid,
                                "ID": elements.ID,
                                "IDF": IDF,
                                "IP": elements.IP,
                            }
                        )
                    )
                )
            )

    async def cancel_oids(self):
        if len(self.tasks) != 0:
            for task in self.tasks:
                task.cancel()
        else:
            return
