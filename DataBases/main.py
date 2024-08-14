import sys
import os
import asyncio
# Añade el directorio raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ifTable import interfaceTable
from fastapi import Depends,FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, and_,null
from sqlalchemy.orm import joinedload

from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import crud,models,schemas
from database import SessionLocal,engine
from Inicial import Inicial
from Manageable import ManageablePC, ManageableRT
from typing import List
import json


models.Base.metadata.create_all(bind=engine)  # crea la base de datos si no existe

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_instance_startup()
    asyncio.create_task(Inicial())
    yield


origins=[
    "http://localhost",
    "http://localhost:8080",
]

instances={}

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def create_instance_startup():
    agents = crud.get_all_agent(db=SessionLocal())
    for agent in agents:
        instance=create_instance_from_Manageable(agent)
        instances[agent.ag_name] = instance
        sensors =  SessionLocal().query(models.Active_default).options(joinedload(models.Active_default.features)).filter(models.Active_default.id_agent == agent.id_agent).all()
        for sensor in sensors:
            params = json.loads(sensor.params)
            await activator_tasks(name=agent.ag_name, nametask=sensor.features.fe_name, params=params)
           


def create_instance_from_Manageable(request: schemas.Agent):
    if request.ag_type ==2:
        return ManageablePC(request.ip_address, request.ag_name, request.id_agent)
    elif request.ag_type == 3:
        return ManageableRT(request.ip_address, request.ag_name,request.id_agent)



async def activator_tasks(name:str, nametask:str, params):
    instance = instances.get(name)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    task_mapping = {
        'saludar': instance.saludar,
        'NumProccesses': instance.NumProccesses,
        'MemorySize': instance.MemorySize
    }

    task_func = task_mapping.get(nametask)
    if not task_func:
        print(f"Tarea no encontrada: {nametask}")
        raise HTTPException(status_code=400, detail="Tarea no encontrada")
    try:
        # Asumiendo que todas las tareas manejan parámetros similares
        params = params
        if nametask in ['NumProccesses', 'MemorySize']:
            await task_func(params, nametask)
            return True
        else:
            await task_func()
    except Exception as e:
        print(f"Error al ejecutar la tarea: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")     




app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

#--------------------------------------------------------------------------------- AGENTES

# recuepra la informacion de todos los agentes
@app.get("/agents/all/", response_model=list[schemas.AgentWithType])
def read_agents(db: Session = Depends(get_db)):
    return crud.get_all_agent(db=db)


# crea agentes
@app.post("/agents/create/",response_model=schemas.Agent)
def create_agent(agent: schemas.CreateAgent, db:Session=Depends(get_db)):
    instance = create_instance_from_Manageable(agent)
    instances[agent.ag_name] = instance
    return crud.create_agent(db=db, agent=agent)

# elimina agentes
@app.delete("/agents/delete/{field}") 
def delete_agent(field:models.ModelField,value, db:Session=Depends(get_db)):
    #instances.pop(field.Hostname)
    print(instances)
    return crud.delete_agent(db=db, field=field.name,value=value)



#---------------------------------------------------------------------------------FEATURES

#Recuepra todas las features(Home)
@app.get("/agents/features/all/", response_model=list[schemas.FeatureswithAgent])
def read_agents(db: Session = Depends(get_db)):
    return crud.get_all_features(db=db)


# recupera todas las features segun el agente(View: Sesnor)
@app.get("/agents/features/agent/{ID}", response_model=list[schemas.FeatureswithAgent])
def read_features(ID,db:Session=Depends(get_db)):
    return crud.get_all_features_agent(db=db,value=ID)

# crea nuevas features(OID)
@app.post("/agents/features/new/",response_model=schemas.Features)
async def new_feature(feature: schemas.new_features, db:Session=Depends(get_db)):
    response = crud.new_feature(db=db, feature=feature)
    await Inicial()
    return response

# Elimina las features
@app.delete("/features/delete/{field}") 
def delete_agent(field:models.ModelFieldSensor,value, db:Session=Depends(get_db)):
    return crud.delete_feature(db=db, field=field.name,value=value)


#---------------------------------------------------------------------------ADICIONALES

# Recupera la iftable del agente en cuestion  (View : Info)
@app.get("/iftable/{host}",response_model=list[schemas.iftable])
async def read_agents(host:str):
    community='public'
    salida = await interfaceTable(community,host)
    return salida



#--------------------------------------------------------------------------------HISTORIAL

#Obtener el historial segun el sensor (OID)
@app.post("/history/sensor/",response_model=schemas.responseHistory)
def read_history_sensor(filter: schemas.getHistory, db:Session=Depends(get_db)):
    return crud.get_history_sensor(db=db, filter=filter)



#-----------------------------------------------------------------------------------GESTIONABLES


@app.get("/features/default/agent/",response_model=list[schemas.ReadDefaultFeature]) 
def get_deafult_feature_agent(id:int,type:int, db:Session=Depends(get_db)):
     
     tareas= db.query(models.Default_features.fe_name,models.Default_features.id_feature).outerjoin(
         models.Active_default,
         and_(
          models.Default_features.id_feature == models.Active_default.id_feature,
          models.Active_default.id_agent == id
          )).filter(
                and_(
                    models.Active_default.id_feature.is_(None) ,
                    models.Default_features.id_type.in_([1,type])
                ))
     return tareas



@app.get("/feature/default/active/",response_model=list[schemas.ReadDefaultFeature]) 
def get_deafult_feature_agent(id:int,type:int, db:Session=Depends(get_db)):
     
     tareas= db.query(models.Default_features.fe_name,models.Default_features.id_feature).join(
         models.Active_default,
          models.Default_features.id_feature == models.Active_default.id_feature).filter(
                and_(
                    models.Active_default.id_agent == id,
                    models.Default_features.id_type.in_([1,type])
                ))
     return tareas



#agregar nueva active a lista de activas
@app.post("/features/deafult/active/new/")
def new_feature(feature: schemas.Addactivedefault, db:Session=Depends(get_db)):
    return crud.add_active_default(db=db, dates=feature)



@app.post("/exect-task/")
async def create_instance(request: schemas.Manageable, db:Session=Depends(get_db)):
    print(request)
    state =await activator_tasks(name=request.name,nametask=request.nametask,params=request.params)       
    if state:
        state = crud.add_active_default(db=db, dates=request)
    else :
        raise HTTPException(status_code=400, detail="Tarea no subida")



#Deteenr una de las atreas por defautl
@app.post("/task/stop/")
async def stop_instance(request:schemas.Manageable,db:Session=Depends(get_db)):
    instance = instances.get(request.name)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    state = crud.delete_active_default(db=db, dates=request)
    await instance.cancelar_tarea( request.nametask)
    await instance.Iniciar()
    return {"result": 'tarea cancelada'}            

#---------------------------------------------------------------------------------PRUEBAS
    
     

@app.get("/tareas activas",response_model=list[schemas.ActiveWithFeature])
async def read_actives(db:Session=Depends(get_db)):
    return crud.get_active_default_prueba(db=db)


@app.post("/pruebaaaasss/")
async def stop_instance(request:schemas.Manageable,db:Session=Depends(get_db)):
    instance = instances.get(request.name)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    await instance.task_oid()


@app.post("/pruebs/")
async def stop_instance(request:schemas.Manageable,db:Session=Depends(get_db)):
    instance = instances.get(request.name)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    await instance.restarttask()