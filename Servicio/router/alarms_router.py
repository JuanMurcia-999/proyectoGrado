from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..schema import alarms_schemas as schema
from ..services import alarms_services as crud

router = APIRouter(prefix="/alarms")


# Eliminar alarmas
@router.get("/all/", tags=["ALARMS"], response_model=list[schema.readAlarm])
async def read_agents(id_agent: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_alarm(db=db, id_agent=id_agent)


# Eliminar las alarmas
@router.delete("/delete/", tags=["ALARMS"])
async def delete_feature(id: int, db: AsyncSession = Depends(get_db)):
    state = await crud.delete_alarm(db=db, id_alarm=id)
    if state:
        raise HTTPException(status_code=200, detail="Alarma Eliminada")
    else:
        raise HTTPException(status_code=400, detail="Alarma ya eliminada")


# Crear alarmas
@router.post("/new/", tags=["ALARMS"])
async def new_alarm(alarm: schema.newAlarm, db: AsyncSession = Depends(get_db)):
    state = await crud.add_alarm(db=db, alarm=alarm)
    if state:
        raise HTTPException(status_code=200, detail="Alarma agregada")
