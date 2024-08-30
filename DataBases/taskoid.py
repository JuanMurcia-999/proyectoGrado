import sys
import os
import asyncio

# Añade el directorio raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
from slim.slim_get import slim_get
import models
import schemas
from Colahistory import HistoryFIFO
from ColaAlarms import AlarmsFIFO
from Gestionables import Ping

# Configuración de la base de datos
DATABASE_URL = "sqlite:///productos.sqlite"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

colaoid = HistoryFIFO()
alarm = AlarmsFIFO()

Af = models.Administered_features


async def Totalagentes(id_agent: int, ip_agent: str):

    db = SessionLocal()
    try:
        TIMES = []
        OIDS = []
        IDF = []

        intervalos = (
            db.query(
                Af.timer,
            )
            .filter(
                Af.id_agent == id_agent,
                Af.oid != "",
            )
            .distinct()
            .all()
        )

        for inter in intervalos:
            TIMES.append(inter.timer)
            features = (
                db.query(
                    Af.oid,
                    Af.id_adminis,
                )
                .filter(
                    Af.timer == f"{inter.timer}",
                    Af.id_agent == id_agent,
                    Af.oid != "",
                )
                .all()
            )

            OIDS.append([item.oid for item in features])
            IDF.append([item.id_adminis for item in features])

        return schemas.elements(
            **{"ID": id_agent, "IP": ip_agent, "TIMES": TIMES, "OIDS": OIDS, "IDF": IDF}
        )
    finally:
        db.close()


async def Get_SNMP(task: schemas.taskoid):
    while True:

        try:
            satate =await Ping().getstate(task.ID)
            if satate:
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

                        record = schemas.addHistory(**datos)
                        colaoid.encolar(record)
                        alarm.encolar(record)
        except Exception:
            return
        finally:
            await asyncio.sleep(task.TIME)


class sensorOID:
    def __init__(self, ip: str, id: int) -> None:
        self.ip = ip
        self.id = id
        self.tasks = []

    async def CreatorTask(self):
        await asyncio.sleep(2)
        for task in self.tasks:
            task.cancel()
        elements = await Totalagentes(self.id, self.ip)
        # print(elements)

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
