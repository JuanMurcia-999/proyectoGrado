from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..schema import manageable_schemas as schema
from ..services.features_services import new_feature
from ..services import manageable_services as crud
from ..database import get_db
from ..function import activator_tasks,instances


router = APIRouter(prefix='')



@router.get(
    "/features/default/agent/",
    tags=["MANAGEABLES"],
    response_model=list[schema.ReadDefaultFeature],
)
async def get_deafult_feature_agent(
    id: int, type: int, db: AsyncSession = Depends(get_db)
):
    return await crud.get_default_features_agent(db=db, id=id, type=type)


@router.get(
    "/feature/default/active/",
    tags=["MANAGEABLES"],
    response_model=list[schema.ReadDefaultFeature],
)
async def get_deafult_feature_agent(
    id: int, type: int, db: AsyncSession = Depends(get_db)
):
    return await crud.get_active_default(db=db, id=id, type=type)


@router.post("/exect-task/", tags=["MANAGEABLES"], status_code=status.HTTP_202_ACCEPTED)
async def create_instance(
    request: schema.Manageable, db: AsyncSession = Depends(get_db)
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

    feature = schema.new_features(**datos)

    await crud.add_active_default(db=db, dates=request)
    state = await activator_tasks(
        name=request.name, nametask=request.nametask, params=request.params
    )
    if request.nametask == "Networktraffic":
        for i in range(0, 2):
            id_sensor = int(
                str(request.params["id_adminis"])
                + str(request.params["num_interface"])
                + f"{i}"
            )
            print(id_sensor)
            feature.id_sensor = id_sensor
            feature.adminis_name = feature.adminis_name + (
                lambda x: "IN" if i == 0 else "OUT"
            )(None)
            await new_feature(db=db, feature=feature)
    else:
        await new_feature(db=db, feature=feature)


# Deteenr una de las atreas por defautl
@router.post("/task/stop/", tags=["MANAGEABLES"], status_code=status.HTTP_202_ACCEPTED)
async def stop_instance(
    request: schema.Manageable, db: AsyncSession = Depends(get_db)
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
        raise HTTPException(status_code=404, detail="Agente inexistente")
    await crud.delete_active_default(db=db, dates=request)
    await crud.delete_feature_two(db=db, name=nametask[0], id=request.id_agent)
    await instance.cancelar_tarea(nametask[0])

