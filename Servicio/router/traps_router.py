from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..services import traps_services as crud
from ..database import get_db


router = APIRouter(prefix="/traps")



@router.get("/all/" ,tags=["TRAPS"])
async def get_traps(db: AsyncSession = Depends(get_db)):
    return await crud.get_all_traps(db=db)


@router.get("/message/{ID}", tags=["TRAPS"])
async def get_trap_message(ID, db: AsyncSession = Depends(get_db)):
    return await crud.get_trap_message(db=db, value=ID)
