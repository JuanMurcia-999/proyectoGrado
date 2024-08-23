import sys
import os
import asyncio

# Añade el directorio raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
from slim.slim_get import slim_get
from slim.slim_bulk import get_bulk
import models
import schemas
from Colahistory import HistoryFIFO
from ColaAlarms import AlarmsFIFO

# Configuración de la base de datos
DATABASE_URL = "sqlite:///C:/Users/Juan Murcia/Desktop/Proyecto de grado/Desarrollo/Recolector/DataBases/productos.sqlite"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

colaoid = HistoryFIFO()
alarm = AlarmsFIFO()


async def Totalagentes(id_agent: int, ip_agent: str):
    allelements = []
    db = SessionLocal()  # Asegúrate de que cada tarea tenga su propia sesión

    try:
        TIMES = []
        OIDS = []
        IDF = []

        intervalos = (
            db.query(
                models.Administered_features.timer,
                models.Administered_features.id_adminis,
            )
            .filter(
                models.Administered_features.id_agent == id_agent,
                models.Administered_features.oid != "",
            )
            .distinct()
            .all()
        )

        for inter in intervalos:
            TIMES.append(inter.timer)
            IDF.append(inter.id_adminis)
            features = (
                db.query(
                    models.Administered_features.oid,
                    models.Administered_features.id_adminis,
                )
                .filter(
                    models.Administered_features.timer == f"{inter.timer}",
                    models.Administered_features.id_agent == id_agent,
                    models.Administered_features.oid != "",
                )
                .all()
            )

            OIDS.append([item.oid for item in features])

        allelements.append(
            {"ID": id_agent, "IP": ip_agent, "TIMES": TIMES, "OIDS": OIDS, "IDF": IDF}
        )
        return allelements
    finally:
        db.close()


async def Get_SNMP(**task):
    while True:
        await asyncio.sleep(task["TIME"])
        varBinds = await get_bulk(
            "public",
            task["IP"],
            161,
            0,
            1,  # nonRepeaters, maxRepetitions
            *task["OIDS"],
        )

        for varBind in varBinds:
            oid, value = varBind[0]
            print(f"{task['TIME']}::::{oid}::: {value.prettyPrint()}::: {task['IP']}")

            datos = {"id_agent": task["ID"], "id_adminis": task["IDF"], "value": value}

            record = schemas.addHistory(**datos)
            colaoid.encolar(record)
            alarm.encolar(record)


class sensorOID:
    def __init__(self, ip: str, id: int) -> None:
        self.ip = ip
        self.id = id
        self.tasks = []

    async def CreatorTask(self):
        for task in self.tasks:
            task.cancel()
        elements = await Totalagentes(self.id, self.ip)
        print(elements)
        for agent in elements:
            for TIME, OIDS, IDF in zip(agent["TIMES"], agent["OIDS"], agent["IDF"]):
                oid = [ObjectType(ObjectIdentity(f"{oid}")) for oid in OIDS]
                self.tasks.append(
                    asyncio.create_task(
                        Get_SNMP(
                            TIME=TIME, OIDS=oid, ID=agent["ID"], IDF=IDF, IP=agent["IP"]
                        )
                    )
                )
        print(self.tasks)


# async def Inicial():
#     Camilo = sensorOID('192.168.20.25', 2)
#     Erika = sensorOID('192.168.20.37', 3)

#     # Ejecuta las tareas de los sensores concurrentemente
#     await asyncio.gather(
#         Camilo.CreatorTask(),
#         Erika.CreatorTask()
#     )

# asyncio.run(Inicial())
