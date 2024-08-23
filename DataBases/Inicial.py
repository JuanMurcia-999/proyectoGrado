import sys
import os
import asyncio

# Añade el directorio raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pysnmp.proto import rfc1902
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
from slim.slim_get import slim_get
from slim.slim_bulk import get_bulk
import models
import asyncio
from datetime import datetime


# Configuración de la base de datos
DATABASE_URL = "sqlite:///C:/Users/Juan Murcia/Desktop/Proyecto de grado/Desarrollo/Recolector/DataBases/productos.sqlite"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()


async def Totalagentes():
    allelements = []
    try:
        # recuperar las ips de todos los agentes
        agents = db.query(models.Agents).all()
        for agent in agents:
            IPS = []
            IDS = []
            TIMES = []
            OIDS = []
            IDF = []
            IDS.append(agent.id_agent)
            IPS.append(agent.ip_address)

            # recuperar los tiempos unicos por cada agente
            intervalos = (
                db.query(
                    models.Administered_features.timer,
                    models.Administered_features.id_adminis,
                )
                .filter(models.Administered_features.id_agent == f"{agent.id_agent}")
                .distinct()
                .all()
            )

            for inter in intervalos:
                TIMES.append(inter.timer)
                IDF.append(inter.id_adminis)
                # Recuperar las features por cada intervalo
                features = (
                    db.query(
                        models.Administered_features.oid,
                        models.Administered_features.id_adminis,
                    )
                    .filter(
                        models.Administered_features.timer == f"{inter.timer}",
                        models.Administered_features.id_agent == f"{agent.id_agent}",
                    )
                    .all()
                )

                OIDS.append([item.oid for (item) in features])
                # IDF.append([item.id_adminis for (item) in features])
            allelements.append(
                {"IPS": IPS, "ID": IDS, "TIMES": TIMES, "OIDS": OIDS, "IDF": IDF}
            )
        # pasar los valores por agente a la funcion que crea los agentes
        await CreatorTask(allelements)
    finally:
        db.close()


async def Get_SNMP(**task):
    while True:
        await asyncio.sleep(task["TIME"])
        varBinds = await get_bulk(
            "public",
            *task["IP"],
            161,
            0,
            1,  # nonRepeaters, maxRepetitions
            *task["OIDS"],
        )

        # for varBindRow in varBindTable:
        for varBind in varBinds:
            oid, value = varBind[0]
            print(
                f"{task['TIME']}::::{oid}::: {value.prettyPrint()}::: {task['IP'][0]}"
            )

            db_history = models.History_features(
                id_agent=str(task["ID"][0]),
                id_adminis=str(str(task["IDF"])),
                value=str(value),
            )

            db.add(db_history)
            state = db.commit()
            print("estado")
            db.refresh(db_history)


async def create_object_types(OIDS):
    return [ObjectType(ObjectIdentity(f"{oid}")) for oid in OIDS]


async def CreatorTask(elements):
    tasks = []
    for agent in elements:
        for TIME, OIDS, IDF in zip(agent["TIMES"], agent["OIDS"], agent["IDF"]):
            oid = await create_object_types(OIDS)
            tasks.append(
                asyncio.create_task(
                    Get_SNMP(
                        TIME=TIME, OIDS=oid, ID=agent["ID"], IDF=IDF, IP=agent["IPS"]
                    )
                )
            )
    await asyncio.gather(*tasks)


# async def Inicial():
#     print("Tarea ")
    # await Totalagentes()


# asyncio.run(Inicial()
