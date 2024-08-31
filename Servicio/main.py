import sys
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Añade el directorio raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from sqlalchemy.future import select
from Utilizables.Gestionables import *
from Utilizables.Manageable import *
from Utilizables.ifTable import interfaceTable
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import joinedload

from contextlib import asynccontextmanager
import crud, models, schemas
from database import SessionLocal, engine, Base
from Abstracciones import *
from colaDos import AsyncFIFOQueue

import json
from Colahistory import HistoryFIFO
from ColaAlarms import AlarmsFIFO

from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Lifespan function started")
    # asyncio.create_task(AsyncFIFOQueue().add(1))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await create_instance_startup()
    # asyncio.create_task(Ping().Exectping())
    print("Lifespan function finished")
    yield
    await Exit_service()




alarms = AlarmsFIFO()

app = FastAPI(lifespan=lifespan)

instances = {}


async def get_db():
    async with SessionLocal() as db:
        yield db

cola = AsyncFIFOQueue(db)

async def Exit_service():
    await SessionLocal().close()
    print(instances)
    for name, proc in instances.items():
        await proc.cancel_end()
    

async def create_instance_startup():
    agents = await crud.get_all_agent(db=db)
    for agent in agents:
        
        await Ping().addagent(agent.id_agent, agent.ip_address)
        instance = await create_instance_from_Manageable(agent)
        instances[agent.ag_name] = instance
        await instance.task_oid()
        sensors = (
            (
                await db.execute(
                    select(models.Active_default)
                    .options(joinedload(models.Active_default.features))
                    .filter(models.Active_default.id_agent == agent.id_agent)
                )
            )
            .scalars()
            .all()
        )
        for sensor in sensors:
            params = json.loads(sensor.params)
            await activator_tasks(
                name=agent.ag_name, nametask=sensor.features.fe_name, params=params
            )


async def create_instance_from_Manageable(request: schemas.Agent):
    await Ping().addagent(request.id_agent, request.ip_address)
    if request.ag_type == 2:
        return ManageablePC(request.ip_address, request.ag_name, request.id_agent)
    elif request.ag_type == 3:
        return ManageableRT(request.ip_address, request.ag_name, request.id_agent)
    elif request.ag_type == 4:
        return ManageableMixto(request.ip_address, request.ag_name, request.id_agent)


async def activator_tasks(name: str, nametask: str, params):
    instance = instances.get(name)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")

    if isinstance(instance, ManageableMixto):
        task_mapping = {
            "NumProccesses": instance.NumProccesses,
            "MemorySize": instance.MemorySize,
            "Networktraffic": instance.Networktraffic,
            "Networktraffic": instance.Networktraffic,
            "MemoryUsed": instance.MemoryUsed,
            "CpuUsed": instance.CpuUsed,
            "DiskUsed": instance.DiskUsed,
        }

    elif isinstance(instance, (ManageablePC, ManageableRT)):
        task_mapping = {
            "NumProccesses": instance.NumProccesses,
            "MemorySize": instance.MemorySize,
            "Networktraffic": instance.Networktraffic,
            "Networktraffic": instance.Networktraffic,
        }
    task_func = task_mapping.get(nametask)
    if not task_func:
        print(f"Tarea no encontrada: {nametask}")
        raise HTTPException(status_code=400, detail="Tarea no encontrada")
    try:
        # Asumiendo que todas las tareas manejan parámetros similares
        params = params
        if nametask in [
            "NumProccesses",
            "MemorySize",
            "Networktraffic",
            "MemoryUsed",
            "CpuUsed",
            "DiskUsed",
        ]:
            await task_func(params, nametask, cola, alarms)
            return True
        else:
            await task_func()
    except Exception as e:
        print(f"Error al ejecutar la tarea: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# --------------------------------------------------------------------------------- AGENTES


# recuepra la informacion de todos los agentes
@app.get("/agents/all/")
async def read_agents(db: AsyncSession = Depends(get_db)):
    return await crud.get_all_agent(db=db)


# Agregar agente
@app.post("/agents/create/")
async def create_agent(agent: schemas.CreateAgent, db: AsyncSession = Depends(get_db)):
    id_agent = await crud.create_agent(db=db, agent=agent)
    if id_agent:
        data = {
            "ag_name": agent.ag_name,
            "ip_address": agent.ip_address,
            "ag_type": agent.ag_type,
            "id_agent": id_agent,
        }
        Agent = schemas.Agent(**data)
        instance = await create_instance_from_Manageable(Agent)
        instances[agent.ag_name] = instance
    else:
        raise HTTPException(status_code=400, detail="ya agregado o error")


# elimina agentes
@app.delete("/agents/delete/{field}")
async def delete_agent(
    field: models.ModelField, value, db: AsyncSession = Depends(get_db)
):
    db_agent = await crud.delete_agent(db=db, field=field.name, value=value)
    if db_agent:
        del instances[db_agent.ag_name]
        await Ping().deleteagent(db_agent.id_agent)
        raise HTTPException(status_code=200, detail="agente eliminado")
    else:
        raise HTTPException(status_code=400, detail="ya eliminado o error")


# ---------------------------------------------------------------------------------FEATURES


# Recuepra todas las features(Home)
@app.get("/agents/features/all/", response_model=list[schemas.FeatureswithAgent])
async def get_all_features(db: AsyncSession = Depends(get_db)):
    return await crud.get_all_features(db=db)


# recupera todas las features segun el agente(View: Sesnor) response_model=list[schemas.FeatureswithAgent]
@app.get("/agents/features/agent/{ID}", response_model=list[schemas.FeatureswithAgent])
async def get_features_agent(ID, db: AsyncSession = Depends(get_db)):
    return await crud.get_all_features_agent(db=db, value=ID)


# crea nuevas features(OID)
@app.post("/agents/features/new/")
async def new_feature(
    feature: schemas.new_features, db: AsyncSession = Depends(get_db)
):
    instance = instances.get(feature.ag_name)
    response = await crud.new_feature(db=db, feature=feature)
    if response:
        await instance.restarttask()
    else:
        raise HTTPException(status_code=400, detail="ya existe o esta desconectado")


# Elimina las features
@app.delete("/features/delete/")
async def delete_feature(id: int, nametask: str, db: AsyncSession = Depends(get_db)):
    instance = instances.get(nametask)
    state = await crud.delete_feature(db=db, id=id)
    if state:
        await instance.restarttask()
    return


# # ---------------------------------------------------------------------------ADICIONALES


# Recupera la iftable del agente en cuestion  (View : Info)
@app.get("/iftable/{host}", response_model=list[schemas.iftable])
async def read_agents(host: str):
    community = "public"
    salida = await interfaceTable(community, host)
    if salida:
        return salida
    else:
        raise HTTPException(status_code=400, detail="No se puede adquirir la iftable")


# # --------------------------------------------------------------------------------HISTORIAL


# Obtener el historial segun el sensor (OID)
@app.post("/history/sensor/")
async def read_history_sensor(
    filter: schemas.getHistory, db: AsyncSession = Depends(get_db)
):
    if filter.id_sensor == 100:
        return await crud.get_history_Network(db=db, filter=filter)
    else:
        return await crud.get_history_sensor(db=db, filter=filter)


@app.post("/history/filter/")
async def read_history_sensor(filter: schemas.filterHistory, db: AsyncSession = Depends(get_db)):
    if filter.id_sensor == 105:
        dato = f"{filter.id_sensor}{filter.id_agent}"
        return await Abtraciones().CPU(dato, filter)
    elif str(filter.id_sensor).startswith("100"):
        return await Abtraciones().NETWORK(filter)
    else:
        return await crud.get_history_filter(db=db, filter=filter)


# # -----------------------------------------------------------------------------------GESTIONABLES


@app.get("/features/default/agent/", response_model=list[schemas.ReadDefaultFeature])
async def get_deafult_feature_agent(
    id: int, type: int, db: AsyncSession = Depends(get_db)
):
    return await crud.get_default_features_agent(db=db, id=id, type=type)


@app.get("/feature/default/active/", response_model=list[schemas.ReadDefaultFeature])
async def get_deafult_feature_agent(
    id: int, type: int, db: AsyncSession = Depends(get_db)
):
    return await crud.get_active_default(db=db, id=id, type=type)


@app.post("/exect-task/")
async def create_instance(
    request: schemas.Manageable, db: AsyncSession = Depends(get_db)
):
    datos = {
        "id_adminis": None,
        "id_sensor": request.params["id_adminis"],
        "ag_name": "",
        "id_agent": request.id_agent,
        "oid": "",
        "adminis_name": (
            lambda x: (
                request.nametask
                if request.nametask != "Networktraffic"
                else request.nametask + request.params["num_interface"]
            )
        )(None),
        "timer": request.params["timer"],
    }

    feature = schemas.new_features(**datos)

    state = await activator_tasks(
        name=request.name, nametask=request.nametask, params=request.params
    )

    if state:
        await crud.add_active_default(db=db, dates=request)
        if request.nametask == "Networktraffic":
            for i in range(0, 2):
                id_sensor = int(
                    str(request.params["id_adminis"])
                    + str(request.params["num_interface"])
                    + f"{i}"
                )
                feature.id_sensor = id_sensor
                feature.adminis_name = feature.adminis_name + (
                    lambda x: "IN" if i == 0 else "OUT"
                )(None)
                await crud.new_feature(db=db, feature=feature)
        else:
            await crud.new_feature(db=db, feature=feature)
    else:
        raise HTTPException(status_code=400, detail="Tarea no subida")


# Deteenr una de las atreas por defautl
@app.post("/task/stop/")
async def stop_instance(
    request: schemas.Manageable, db: AsyncSession = Depends(get_db)
):
    instance = instances.get(request.name)
    nametask = (
        (
            lambda x: (
                request.nametask
                if request.nametask != "Networktraffic"
                else request.nametask + request.params["num_interface"]
            )
        )(None),
    )
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    state1 = await crud.delete_active_default(db=db, dates=request)
    state2 = await crud.delete_feature_two(db=db, name=nametask[0], id=request.id_agent)
    await instance.cancelar_tarea(nametask[0])
    # await instance.Iniciar()
    return {"result": "tarea cancelada"}


# # --------------------------------------------------------------------------------- ALARMAS


# Eliminar alarmas
@app.get("/alarms/all/", response_model=list[schemas.readAlarm])
async def read_agents(id_agent: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_alarm(db=db, id_agent=id_agent)


# Eliminar las alarmas
@app.delete("/alarms/delete/")
async def delete_feature(id: int, db: AsyncSession = Depends(get_db)):
    state = await crud.delete_alarm(db=db, id_alarm=id)
    if state:
        raise HTTPException(status_code=200, detail="Alarma Eliminada")
    else:
        raise HTTPException(status_code=400, detail="Alarma ya eliminada")


# Crear alarmas
@app.post("/alarms/new/")
async def new_alarm(alarm: schemas.newAlarm, db: AsyncSession = Depends(get_db)):
    state = await crud.add_alarm(db=db, alarm=alarm)
    if state:
        raise HTTPException(status_code=200, detail="Alarma agregada")


# # --------------------------------------------------------------------------------------------------WebSocket
# # data_store: Dict[str, List[dict]] = {}

# # @app.websocket("/ws")
# # async def websocket_endpoint(websocket: WebSocket):
# #     await websocket.accept()
# #     try:
# #         while True:
# #             data = await websocket.receive_json()
# #             await websocket.send_json({"message": "Data received", "data": data})
# #     except WebSocketDisconnect:
# #         await websocket.close()


# # ---------------------------------------------------------------------------------PRUEBAS
