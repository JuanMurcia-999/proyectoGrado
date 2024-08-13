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

models.Base.metadata.create_all(bind=engine)  # crea la base de datos si no existe

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_instance_startup()
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

def create_instance_startup():
    agents = crud.get_all_agent(db=SessionLocal())
    for agent in agents:
        instance=create_instance_from_Manageable(agent)
        instances[agent.ag_name] = instance
        print(instance)
    
    


def create_instance_from_Manageable(request: schemas.Agent):
    if request.ag_type ==2:
        return ManageablePC(request.ip_address, request.ag_name)
    elif request.ag_type == 3:
        return ManageableRT(request.ip_address, request.ag_name)


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
    print(instance)
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
#Agrega infromacion al historial(Temporal)
@app.post("/history/add/")
def add_history(record: schemas.addHistory, db:Session=Depends(get_db)):
    return crud.add_history(db=db, record=record)

#Recuepara todo el historial de todos los sensores (Temporal)
@app.post("/history/all/",response_model=list[schemas.readHistory])
def add_history(db:Session=Depends(get_db)):
    return crud.get_all_history (db=db)

#Obtener el historial segun el sensor (OID)
@app.post("/history/sensor/",response_model=schemas.responseHistory)
def read_history_sensor(filter: schemas.getHistory, db:Session=Depends(get_db)):
    return crud.get_history_sensor(db=db, filter=filter)



#-----------------------------------------------------------------------------------GESTIONABLES

#crear nuevo gestionable (TEMPORAL)
@app.post("/features/deafult/new/",response_model=schemas.addDefaultFeature)
def new_feature(feature: schemas.addDefaultFeature, db:Session=Depends(get_db)):
    return crud.add_default_feature(db=db, feature=feature)


# Obtener los default segun el tipo de agente
# @app.get("/features/default/agent/",response_model=list[schemas.addDefaultFeature]) 
# def get_deafult_feature_agent(value:str, db:Session=Depends(get_db)):
#     return crud.get_all_default_features(db=db,value=value)


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




# # Obtener el listado de las tareas default activas 
# @app.get("/feature/default/active/", response_model=list[schemas.ReadAddactivedefault])
# def get_active_default(value:str , db:Session=Depends(get_db)):
#     return crud.get_active_default(db=db, value=value)

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


# Ejecutar una de las tareas por default 
@app.post("/exect-task/")
async def create_instance(request: schemas.Manageable, db:Session=Depends(get_db)):
    print(request)
    instance = instances.get(request.name)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    if request.nametask =='Networktraffic':
         await instance.Networktraffic(str(request.params['inter']),request.params['timer'], request.params['task'])
    elif request.nametask =='saludar':
        await instance.saludar()
    elif request.nametask == 'NumProccesses':
        await instance.NumProccesses(request.params['timer']|10, request.params['task'])
    elif request.nametask == 'MemorySize':
        await instance.MemorySize(request.params['timer'], request.params['task'])
    state = crud.add_active_default(db=db, dates=request.params)    
    return {"result": 'Instancia creada'}


#Deteenr una de las atreas por defautl
@app.post("/task/stop/")
async def stop_instance(request:schemas.Manageable,db:Session=Depends(get_db)):
    print(request)
    instance = instances.get(request.name)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    state = crud.delete_active_default(db=db, dates=request.params)
    instance.cancelar_tarea( request.params['task'])
    await instance.Iniciar()
    
    
     
    return {"result": 'tarea cancelada'}


#---------------------------------------------------------------------------------PRUEBAS


@app.get("/activas/",response_model=list[schemas.ReadDefaultFeature]) 
def get_deafult_feature_agent(value:int, db:Session=Depends(get_db)):
     
     tareas= db.query(models.Default_features.fe_name,models.Default_features.id_feature).join(
         models.Active_default,
          models.Default_features.id_feature == models.Active_default.id_feature).filter(
                and_(
                    models.Active_default.id_agent == value,
                    models.Default_features.id_type.in_([1,2])
                ))
     return tareas

@app.get("/Disponibles/",response_model=list[schemas.ReadDefaultFeature]) 
def get_deafult_feature_agent(value:int, db:Session=Depends(get_db)):
     
     tareas= db.query(models.Default_features.fe_name,models.Default_features.id_feature).outerjoin(
         models.Active_default,
         and_(
          models.Default_features.id_feature == models.Active_default.id_feature,
          models.Active_default.id_agent ==  value
          )).filter(
                and_(
                    models.Active_default.id_feature.is_(None) ,
                    models.Default_features.id_type.in_([1,2])
                ))
     return tareas





@app.post("/pruebassssssss/")
async def stop_instance(request:schemas.Manageable,db:Session=Depends(get_db)):

    state = crud.delete_active_default(db=db, dates=request.params)
     
    return state
