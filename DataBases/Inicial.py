import sys
import os
import asyncio
# Añade el directorio raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
    allelements=[]
    try:
        #recuperar las ips de todos los agentes
        agents =db.query(models.Agents).all()
        for agent in agents:
            IPS=[]
            TIMES=[]
            OIDS=[]
            IPS.append(agent.ip_address)
        #recuperar los tiempos unicos por cada agente
            intervalos = db.query(models.Administered_features.timer).filter(models.Administered_features.id_agent == f'{agent.id_agent}').distinct().all()
            for inter in intervalos:
                TIMES.append(inter.timer)
                #Recuperar las features por cada intervalo
                features = db.query(models.Administered_features.oid).filter(models.Administered_features.timer == f'{inter.timer}', models.Administered_features.id_agent == f'{agent.id_agent}').all()
                OIDS.append( [item for (item,) in features])
            allelements.append(
                 {
                      "IP":IPS,
                      "TIMES": TIMES,
                      "OIDS":OIDS
                 }
            )
        #pasar los valores por agente a la funcion que crea los agentes   
        
        #await CreatorTask(allelements)
    finally:
        db.close()

async def Get_SNMP(**task):
    while True:    
        await asyncio.sleep(task['TIME'])
        varBinds = await get_bulk(
            'public',*task['IP'] , 161,
            0, 1,  # nonRepeaters, maxRepetitions
           *task['OIDS']
        )
        
        #for varBindRow in varBindTable:
        for varBind in varBinds:
            oid, value = varBind[0]
            print(f"{task['TIME']}::::{oid}::: {value.prettyPrint()}::: {task['IP'][0]}")

            db_history= models.History_features  (
            ip_agent=str(task['IP'][0]),
            oid=str(oid),
            value=str(value)
            )

            db.add(db_history)
            db.commit()
            db.refresh(db_history)
    
async def create_object_types(OIDS):
    return [ObjectType(ObjectIdentity(f'{oid}')) for oid in OIDS]

async def CreatorTask(elements):
    tasks=[]
    for agent in elements:
        for TIME,OIDS in zip(agent['TIMES'],agent['OIDS']):
            oid = await create_object_types(OIDS)
            tasks.append(asyncio.create_task(Get_SNMP(TIME=TIME,OIDS=oid,IP=agent['IP'])))
    await asyncio.gather(*tasks)
   



async def pruebas():
    response = db.query(models.History_features.value,models.History_features.created_at).filter(models.History_features.oid == '1.3.6.1.2.1.2.2.1.10.12'  ,models.History_features.ip_agent == '192.168.20.25')
    values = [item[0] for item in response]
    date =  [item[1].strftime('%Y-%m-%d %H:%M:%S')    for item in response]

    #print(values)
    #print(type(date[0]))

async def Inicial():
    #await pruebas()
    await Totalagentes()
    print('Funcion inicial')
#asyncio.run(Inicial())