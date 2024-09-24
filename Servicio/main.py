import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from Utilizables.Gestionables import *
from Utilizables.Manageable import *
from Utilizables.ifTable import interfaceTable
from Utilizables.Register import Writer,Read
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
import crud, models, schemas
from database import engine, Base, get_db
from Abstracciones import *
import json
from datetime import datetime
import time
from sqlalchemy.ext.asyncio import AsyncSession
from slim.slim_set import Set

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Lifespan function started")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await create_instance_startup()
    # asyncio.create_task(Ping().Exectping())
    print("Lifespan function finished")
    await Read()
    try:
        Writer(f"\ndatestartup = : {datetime.now()}\n")
        start_time = time.time()
        yield
    finally:
        end_time = time.time()
        Writer(f"datestop = : {datetime.now()}\n")
        Writer(f"totaltime = {end_time - start_time}\n\n")
        await Exit_service()


app = FastAPI(lifespan=lifespan)

instances = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def Exit_service():
    for name, proc in instances.items():
        await proc.cancel_end()


async def create_instance_startup():
    async for db in get_db():
        agents = await crud.get_all_agent(db=db)
    for agent in agents:

        # await Ping().addagent(agent.id_agent, agent.ip_address)
        instance = await create_instance_from_Manageable(agent)
        instances[agent.ag_name] = instance
        await instance.task_oid()
        sensors = await crud.get_sensors_startup(agent.id_agent)

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
            "MemoryUsed": instance.MemoryUsed,
            "CpuUsed": instance.CpuUsed,
            "DiskUsed": instance.DiskUsed,
        }

    elif isinstance(instance, (ManageablePC)):
        task_mapping = {
            "NumProccesses": instance.NumProccesses,
            "MemorySize": instance.MemorySize,
            "Networktraffic": instance.Networktraffic,
        }
    elif isinstance(instance, (ManageableRT)):
        task_mapping = {
            "Networktraffic": instance.Networktraffic,
        }
    task_func = task_mapping.get(nametask)
    if not task_func:
        print(f"Tarea no encontrada: {nametask}")
        raise HTTPException(status_code=400, detail="Tarea no encontrada")
    try:
        params = params
        if nametask in [
            "NumProccesses",
            "MemorySize",
            "Networktraffic",
            "MemoryUsed",
            "CpuUsed",
            "DiskUsed",
        ]:
            await task_func(params, nametask)
            return True
        else:
            await task_func()
    except Exception as e:
        print(f"Error al ejecutar la tarea: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# --------------------------------------------------------------------------------- AGENTES


# recuepra la informacion de todos los agentes
@app.get("/agents/all/" , tags=["AGENTS"])
async def read_agents(db: AsyncSession = Depends(get_db)):
    return await crud.get_all_agent(db=db)


# Agregar agente
@app.post("/agents/create/", tags=["AGENTS"])
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
        await instance.task_oid()
    else:
        raise HTTPException(status_code=400, detail="ya agregado o error")


# elimina agentes
@app.delete("/agents/delete/{field}", tags=["AGENTS"])
async def delete_agent(
    field: models.ModelField, value, db: AsyncSession = Depends(get_db)
):
    db_agent = await crud.delete_agent(db=db, field=field.name, value=value)
    if db_agent:
        instance = instances.get(db_agent.ag_name)
        await instance.cancel_end()
        del instances[db_agent.ag_name]
        await Ping().deleteagent(db_agent.id_agent)
        raise HTTPException(status_code=200, detail="agente eliminado")
    else:
        raise HTTPException(status_code=400, detail="ya eliminado o error")


# ---------------------------------------------------------------------------------FEATURES


# Recuepra todas las features(Home)
@app.get("/agents/features/all/", tags=["FEATURES"],response_model=list[schemas.FeatureswithAgent])
async def get_all_features(db: AsyncSession = Depends(get_db)):
    return await crud.get_all_features(db=db)


# recupera todas las features segun el agente(View: Sesnor) response_model=list[schemas.FeatureswithAgent]
@app.get("/agents/features/agent/{ID}", tags=["FEATURES"],  response_model=list[schemas.FeatureswithAgent])
async def get_features_agent(ID, db: AsyncSession = Depends(get_db)):
    return await crud.get_all_features_agent(db=db, value=ID)


# crea nuevas features(OID)
@app.post("/agents/features/new/", tags=["FEATURES"])
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
@app.delete("/features/delete/" ,tags=["FEATURES"])
async def delete_feature(id: int, nametask: str, db: AsyncSession = Depends(get_db)):
    instance = instances.get(nametask)
    state = await crud.delete_feature(db=db, id=id)
    if state:
        await instance.restarttask()
    return


# # ---------------------------------------------------------------------------ADICIONALES


# Recupera la iftable del agente en cuestion  (View : Info)
@app.get("/iftable/{host}", tags=["ADICIONALES"],response_model=list[schemas.iftable])
async def read_agents(host: str):
    community = "public"
    salida = await interfaceTable(community, host)
    if salida:
        return salida
    else:
        raise HTTPException(status_code=400, detail="No se puede adquirir la iftable")

@app.post("/snmp/set/")
async def new_feature(operation: schemas.operation):
    state = await  Set('public',operation.ip,161,operation.oid,operation.value)
    if not state:
        raise HTTPException(status_code=400, detail="ya existe o esta desconectado")
    

@app.post("/snmp/get/")
async def new_feature(operation: schemas.operation):
    print(operation)
    oid =  ObjectType(ObjectIdentity(operation.oid))
    state = await slim_get('public', operation.ip,161,oid )
    if state:
        _,value=state[0]
        return value
    else:
        raise HTTPException(status_code=400, detail="ya existe o esta desconectado")




# # --------------------------------------------------------------------------------HISTORIAL


# Obtener el historial segun el sensor (OID)
@app.post("/history/sensor/",tags=["ADICIONALES"])
async def read_history_sensor(
    filter: schemas.getHistory, db: AsyncSession = Depends(get_db)
):
    if filter.id_sensor == 100:
        return await crud.get_history_Network(db=db, filter=filter)
    else:
        return await crud.get_history_sensor(db=db, filter=filter)


@app.post("/history/filter/",tags=["ADICIONALES"])
async def read_history_sensor(
    filter: schemas.filterHistory, db: AsyncSession = Depends(get_db)
):
    if filter.id_sensor == 105:
        dato = f"{filter.id_sensor}{filter.id_agent}"
        return await Abtraciones().CPU(dato, filter)
    elif str(filter.id_sensor).startswith("100"):
        return await Abtraciones().NETWORK(filter)
    else:
        return await crud.get_history_filter(db=db, filter=filter)


# # -----------------------------------------------------------------------------------GESTIONABLES


@app.get("/features/default/agent/", tags=["GESTIONABLES"], response_model=list[schemas.ReadDefaultFeature])
async def get_deafult_feature_agent(
    id: int, type: int, db: AsyncSession = Depends(get_db)
):
    return await crud.get_default_features_agent(db=db, id=id, type=type)


@app.get("/feature/default/active/", tags=["GESTIONABLES"], response_model=list[schemas.ReadDefaultFeature])
async def get_deafult_feature_agent(
    id: int, type: int, db: AsyncSession = Depends(get_db)
):
    return await crud.get_active_default(db=db, id=id, type=type)


@app.post("/exect-task/",tags=["GESTIONABLES"])
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
@app.post("/task/stop/", tags=["GESTIONABLES"])
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
@app.get("/alarms/all/", tags=["ALARMS"],response_model=list[schemas.readAlarm])
async def read_agents(id_agent: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_alarm(db=db, id_agent=id_agent)


# Eliminar las alarmas
@app.delete("/alarms/delete/",tags=["ALARMS"])
async def delete_feature(id: int, db: AsyncSession = Depends(get_db)):
    state = await crud.delete_alarm(db=db, id_alarm=id)
    if state:
        raise HTTPException(status_code=200, detail="Alarma Eliminada")
    else:
        raise HTTPException(status_code=400, detail="Alarma ya eliminada")


# Crear alarmas
@app.post("/alarms/new/",tags=["ALARMS"])
async def new_alarm(alarm: schemas.newAlarm, db: AsyncSession = Depends(get_db)):
    state = await crud.add_alarm(db=db, alarm=alarm)
    if state:
        raise HTTPException(status_code=200, detail="Alarma agregada")



#---------------------------------------------------------------------------------------------------- Traps

@app.get("/traps/all/")
async def get_traps(db: AsyncSession = Depends(get_db)):
    return await crud.get_all_traps(db=db)

@app.get("/traps/message/{ID}")
async def get_trap_message(ID, db: AsyncSession = Depends(get_db)):
    return await crud.get_trap_message(db=db, value=ID)



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
