import sys
import os
import asyncio
# Añade el directorio raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
from slim.slim_get import slim_get
import models
import asyncio


# Configuración de la base de datos
DATABASE_URL = "sqlite:///C:/Users/Juan Murcia/Desktop/Proyecto de grado/Desarrollo/Recolector/DataBases/productos.sqlite"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()


async def Totalagentes():
    allelements=[]
    try:
        #recuperar las ips de todos los agentes
        agents =db.query(models.Agents.IP_address).all()
        for agent in agents:
            IPS=[]
            TIMES=[]
            OIDS=[]
            IPS.append(agent.IP_address)
        #recuperar los tiempos unicos por cada agente
            intervalos = db.query(models.Managed_features.timer).filter(models.Managed_features.ip_agent == f'{agent.IP_address}').distinct().all()
            for inter in intervalos:
                TIMES.append(inter.timer)
                #Recuperar las features por cada intervalo
                features = db.query(models.Managed_features.oid).filter(models.Managed_features.timer == f'{inter.timer}', models.Managed_features.ip_agent == f'{agent.IP_address}').all()
                OIDS.append( [item for (item,) in features])
                
                #pasar los valores por agente a la funcion que crea los agentes
            allelements.append(
                 {
                      "IP":f"{agent.IP_address}",
                      "TIMES": TIMES,
                      "OIDS":OIDS
                 }
            )
        await CreatorTask(allelements)
    finally:
        db.close()

async def Get_SNMP(**task):
        varbinds = await slim_get(
        'public', '192.168.20.25', 161,
        ObjectType(ObjectIdentity('1.3.6.1.2.1.2.1.0'))
    )
        
        _, num_registers = varbinds[0]
        print(num_registers)

        await asyncio.sleep(task['TIME'])
        print(f"TIMER : {task['TIME']} , ATRIBUTOS: {task['OIDS']}")
    
async def create_object_types(OIDS):
    return [ObjectType(ObjectIdentity(f'{oid}')) for oid in OIDS]

async def CreatorTask(elements):
    print('Iniciador de tareas')
    tasks=[]
    for agent in elements:
        for time,OIDS in zip(agent['TIMES'],agent['OIDS']):
            oid = await create_object_types(OIDS)
            tasks.append(asyncio.create_task(Get_SNMP(TIME=time,OIDS=OIDS)))
    await asyncio.gather(*tasks)
   



async def Inicial():
    await Totalagentes()

asyncio.run(Inicial())






