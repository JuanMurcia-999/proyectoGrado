import sys
import os
import asyncio
# Añade el directorio raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ifTable import interfaceTable
from fastapi import Depends,FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
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



@app.get("/agents/all/", response_model=list[schemas.AgentWithType])
def read_agents(db: Session = Depends(get_db)):
    agents = db.query(models.Agents).options(joinedload(models.Agents.type)).all()
    return agents

@app.post("/agents/create/",response_model=schemas.Agent)
def create_agent(agent: schemas.CreateAgent, db:Session=Depends(get_db)):
    instance = create_instance_from_Manageable(agent)
    instances[agent.ag_name] = instance
    print(instance)
    return crud.create_agent(db=db, agent=agent)


@app.delete("/agents/delete/{field}") 
def delete_agent(field:models.ModelField,value, db:Session=Depends(get_db)):
    #instances.pop(field.Hostname)
    print(instances)
    return crud.delete_agent(db=db, field=field.name,value=value)

@app.get("/agents/features/all/", response_model=list[schemas.FeatureswithAgent])
def read_agents(db: Session = Depends(get_db)):
    features = db.query(models.Administered_features).options(joinedload(models.Administered_features.agent)).all()
    return features


@app.post("/agents/features/new/",response_model=schemas.Features)
def new_feature(feature: schemas.new_features, db:Session=Depends(get_db)):
    return crud.new_feature(db=db, feature=feature)

@app.delete("/features/delete/{field}") 
def delete_agent(field:models.ModelFieldSensor,value, db:Session=Depends(get_db)):
    return crud.delete_feature(db=db, field=field.name,value=value)


@app.get("/agents/features/agent/{ID}", response_model=list[schemas.Features])
def read_features(ID,db:Session=Depends(get_db)):
    features=crud.get_all_features_agent(db=db,value=ID)
    return features

@app.get("/iftable/{host}",response_model=list[schemas.iftable])
async def read_agents(host:str):
    community='public'
    salida = await interfaceTable(community,host)
    return salida

@app.post("/history/add/")
def add_history(record: schemas.addHistory, db:Session=Depends(get_db)):
    return crud.add_history(db=db, record=record)


@app.post("/history/all/",response_model=list[schemas.readHistory])
def add_history(db:Session=Depends(get_db)):
    return crud.get_all_history (db=db)

@app.post("/history/sensor/",response_model=schemas.responseHistory)
def read_history_sensor(filter: schemas.getHistory, db:Session=Depends(get_db)):
    return crud.get_history_sensor(db=db, filter=filter)


# Gestionables por defecto

@app.post("/features/deafult/new/",response_model=schemas.addDefaultFeature)
def new_feature(feature: schemas.addDefaultFeature, db:Session=Depends(get_db)):
    return crud.add_default_feature(db=db, feature=feature)


@app.get("/features/default/agent/",response_model=list[schemas.addDefaultFeature]) 
def get_deafult_feature_agent(value:str, db:Session=Depends(get_db)):
    return crud.get_all_default_features(db=db,value=value)


@app.post("/exect-task/")
async def create_instance(request: schemas.Manageable):
    instance = instances.get(request.name)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    await instance.saludar()
    await instance.Networktraffic('12', 10, request.nametask)
    return {"result": 'Instancia creada'}


@app.post("/task/stop/")
async def stop_instance(request:schemas.stoptask):
    instance = instances.get(request.name)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    instance.cancelar_tarea(request.nametask)
    await instance.Iniciar()
    return {"result": 'tarea cancelada'}
