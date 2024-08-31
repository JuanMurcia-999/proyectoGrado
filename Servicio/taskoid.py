import sys
import os
import asyncio

# Añade el directorio raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from sqlalchemy.future import select
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
from slim.slim_get import slim_get
import models
import schemas
from Colahistory import HistoryFIFO
from ColaAlarms import AlarmsFIFO
from colaDos import AsyncFIFOQueue
from Utilizables.Gestionables import Ping
from database import SessionLocal



# db = SessionLocal()

# colaoid =AsyncFIFOQueue()
# alarm = AlarmsFIFO(db)

Af = models.Administered_features

# async def some_database_task():
#     async with get_db() as db:
#         yield db
        
async def get_db():
    async with SessionLocal() as db:
        yield db


async def Totalagentes(id_agent: int, ip_agent: str):
    async for db in get_db():
        try:
            TIMES = []
            OIDS = []
            IDF = []

            intervalos = (
                (
                    await db.execute(
                        select(Af.timer)
                        .filter(
                            Af.id_agent == id_agent,
                            Af.oid != "",
                        )
                        .distinct()
                    )
                )
                .scalars()
                .all()
            )

            for inter in intervalos:
                TIMES.append(inter)
                features = (
                    await db.execute(
                        select(Af.oid, Af.id_adminis).filter(
                            Af.timer == f"{inter}",
                            Af.id_agent == id_agent,
                            Af.oid != "",
                        )
                    )
                ).all()

                OIDS.append([item.oid for item in features])
                IDF.append([item.id_adminis for item in features])

            return schemas.elements(
                **{"ID": id_agent, "IP": ip_agent, "TIMES": TIMES, "OIDS": OIDS, "IDF": IDF}
            )
        except Exception:
            print('aglo paso en TotalAgentes')
        finally:
            pass
            # await db.close()


async def Get_SNMP(task: schemas.taskoid):
    while True:
        async for db in get_db():        
            try:
                state = await Ping().getstate(task.ID)
                if False:
                    # print("es verdad y aqui me quedo")
                    # await asyncio.sleep(task.TIME)
                    varbinds = await slim_get("public", task.IP, 161, *task.OIDS)
                    if varbinds:
                        for cosa, id in zip(varbinds, task.IDF):
                            _, value = cosa
                            # print(f"{value}:::::: {id}")

                            datos = {
                                "id_agent": task.ID,
                                "id_adminis": id,
                                "value": round(float(value), 3),
                            }

                            data = schemas.addHistory(**datos)

                            await AsyncFIFOQueue(db).add(data)
                            # await colaoid.add(record)
                            # await alarm.encolar(record)
                            # await asyncio.sleep(task.TIME)
               
            except (asyncio.CancelledError,KeyboardInterrupt):
                await db.close()
                print('fallo en OID')
                break
            finally:
                try:
                    print('esperando oid')
                    await asyncio.sleep(task.TIME)
                except (asyncio.CancelledError,KeyboardInterrupt):
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
        for TIME, OIDS, IDF in zip(elements.TIMES, elements.OIDS, elements.IDF):
            oid = [ObjectType(ObjectIdentity(f"{oid}")) for oid in OIDS]
            self.tasks.append(
                asyncio.create_task(
                    Get_SNMP(
                        schemas.taskoid(
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
        else: return