from fastapi import HTTPException
from .Utils.ifTable import interfaceTable
from .Utils.Manageable import ManageablePC, ManageableRT, ManageableMixto
from .Utils.Gestionables import Ping
from .services.agents_services import get_all_agent
from .database import get_db
from .services import function_services as crud
from .schema.agents_schemas import Agent
import json


instances = {}
iftables = {}


async def Exit_service():
    for name, proc in instances.items():
        await proc.cancel_end()


async def Chargeiftable(ip):
    iftable = await interfaceTable("public", ip)
    if iftables:
        iftables[ip] = iftable


async def create_instance_startup():
    async for db in get_db():
        agents = await get_all_agent(db=db)
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


async def create_instance_from_Manageable(request: Agent):
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
