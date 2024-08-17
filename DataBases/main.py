import sys
import os
import asyncio
# Añade el directorio raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ifTable import interfaceTable
from fastapi import Depends,FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import joinedload

from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import crud,models,schemas
from database import SessionLocal,engine
from Manageable import ManageablePC, ManageableRT

import json
from Colahistory import HistoryFIFO


models.Base.metadata.create_all(bind=engine)  # crea la base de datos si no existe

cola =  HistoryFIFO() 


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_instance_startup()
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
        await instance.task_oid()
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
        'MemorySize': instance.MemorySize,
        'Networktraffic':instance.Networktraffic
    }

    task_func = task_mapping.get(nametask)
    if not task_func:   
        print(f"Tarea no encontrada: {nametask}")
        raise HTTPException(status_code=400, detail="Tarea no encontrada")
    try:
        # Asumiendo que todas las tareas manejan parámetros similares
        params = params
        if nametask in ['NumProccesses', 'MemorySize','Networktraffic']:
            await task_func(params, nametask,cola)
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
    #instance = create_instance_from_Manageable(agent)
    #instances[agent.ag_name] = instance
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
def get_all_features(db: Session = Depends(get_db)):
    return crud.get_all_features(db=db)


# recupera todas las features segun el agente(View: Sesnor)
@app.get("/agents/features/agent/{ID}", response_model=list[schemas.FeatureswithAgent])
def get_features_agent(ID,db:Session=Depends(get_db)):
    return crud.get_all_features_agent(db=db,value=ID)

# crea nuevas features(OID)
@app.post("/agents/features/new/",response_model=schemas.Features)
async def new_feature(feature: schemas.new_features, db:Session=Depends(get_db)):
    instance = instances.get(feature.ag_name)
    response = crud.new_feature(db=db, feature=feature)
    if response:
        await instance.restarttask()
    return response


# Elimina las features
@app.delete("/features/delete/") 
async def delete_feature(id:int, nametask:str, db:Session=Depends(get_db)):
    print(f'{nametask}::::{id}')
    instance = instances.get(nametask)
    state = crud.delete_feature(db=db, id=id)
    if state:
        await instance.restarttask()
    return 

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
    return crud.get_default_features_agent(db=db, id=id,type=type)



@app.get("/feature/default/active/",response_model=list[schemas.ReadDefaultFeature]) 
def get_deafult_feature_agent(id:int,type:int, db:Session=Depends(get_db)):
    return crud.get_active_default(db=db, id=id, type=type)



@app.post("/exect-task/")
async def create_instance(request: schemas.Manageable, db:Session=Depends(get_db)):
    print(request)
    
    datos = {
        "id_adminis": request.params['id_adminis'],
        "ag_name": "",
        "id_agent": request.id_agent,
        "oid": "",
        "adminis_name": (
            lambda x: request.nametask if request.nametask != 'Networktraffic' 
            else request.nametask + request.params['num_interface']
        )(None),  
        "timer": request.params['timer']
    }

    feature = schemas.new_features(**datos)

    state =await activator_tasks(name=request.name,nametask=request.nametask,params=request.params)       
    if state:
        pass
        crud.add_active_default(db=db, dates=request)
        crud.new_feature(db=db, feature=feature)
    else :
        raise HTTPException(status_code=400, detail="Tarea no subida")



#Deteenr una de las atreas por defautl
@app.post("/task/stop/")
async def stop_instance(request:schemas.Manageable,db:Session=Depends(get_db)):
    instance = instances.get(request.name)
    nametask=(
            lambda x: request.nametask if request.nametask != 'Networktraffic' 
            else request.nametask + request.params['num_interface']
        )(None), 
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    state1 = crud.delete_active_default(db=db, dates=request)
    state2 = crud.delete_feature_two(db=db,name =nametask[0],id=request.id_agent)
    await instance.cancelar_tarea(nametask[0])
    await instance.Iniciar()
    return {"result": 'tarea cancelada'}            

#---------------------------------------------------------------------------------PRUEBAS
    
     
