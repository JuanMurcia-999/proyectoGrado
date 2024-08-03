import sys
import os
import asyncio
# Añade el directorio raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from contextlib import asynccontextmanager
from ifTable import interfaceTable
from fastapi import Depends,FastAPI,HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import crud,models,schemas
from database import SessionLocal,engine
from Inicial import Inicial
from fastapi import FastAPI

models.Base.metadata.create_all(bind=engine)  # crea la base de datos si no existe

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(Inicial())
    yield

origins=[
    "http://localhost",
    "http://localhost:8080",
]




def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()


    
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/agents/all/",response_model=list[schemas.Agent])
def read_agents(db:Session=Depends(get_db)):
    agents = crud.get_all_agent(db=db)
    return agents

@app.post("/agents/create/",response_model=schemas.Agent)
def create_agent(agent: schemas.CreateAgent, db:Session=Depends(get_db)):
    return crud.create_agent(db=db, agent=agent)

@app.delete("/agents/delete/{field}") 
def delete_agent(field:models.ModelField,value, db:Session=Depends(get_db)):
    return crud.delete_agent(db=db, field=field.name,value=value)


    
# Endpoint de los features
@app.get("/agents/features/all/", response_model=list[schemas.Features])
def read_features(db:Session=Depends(get_db)):
    features=crud.get_all_features(db=db)
    return features

@app.post("/agents/features/new/",response_model=schemas.Features)
def new_feature(feature: schemas.new_features, db:Session=Depends(get_db)):
    return crud.new_feature(db=db, feature=feature)

@app.delete("/features/delete/{field}") 
def delete_agent(field:models.ModelFieldSensor,value, db:Session=Depends(get_db)):
    return crud.delete_feature(db=db, field=field.name,value=value)

@app.get("/agents/features/agent/{IP}", response_model=list[schemas.Features])
def read_features(IP,db:Session=Depends(get_db)):
    features=crud.get_all_features_agent(db=db,value=IP)
    return features

@app.get("/iftable/{host}",response_model=list[schemas.iftable])
async def read_agents(host:str):
    community='public'
    salida = await interfaceTable(community,host)
    return salida