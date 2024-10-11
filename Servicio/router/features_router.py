from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..function import instances
from ..schema import features_schemas as schema
from ..services import features_services as crud


router = APIRouter(prefix="/agents/features")


# Recuepra todas las features(Home)
@router.get(
    "/all/",
    tags=["FEATURES"],
    response_model=list[schema.FeatureswithAgent],
)
async def get_all_features(db: AsyncSession = Depends(get_db)):
    return await crud.get_all_features(db=db)


# recupera todas las features segun el agente(View: Sesnor) response_model=list[schemas.FeatureswithAgent]
@router.get(
    "/agent/{ID}",
    tags=["FEATURES"],
    response_model=list[schema.FeatureswithAgent],
)
async def get_features_agent(ID, db: AsyncSession = Depends(get_db)):
    return await crud.get_all_features_agent(db=db, value=ID)


# crea nuevas features(OID)
@router.post("/new/", tags=["FEATURES"])
async def new_feature(feature: schema.new_features, db: AsyncSession = Depends(get_db)):
    instance = instances.get(feature.ag_name)
    response = await crud.new_feature(db=db, feature=feature)
    if response:
        await instance.restarttask()
    else:
        raise HTTPException(status_code=400, detail="ya existe o esta desconectado")


# Elimina las features
@router.delete(
    "/features/delete/", tags=["FEATURES"], status_code=status.HTTP_202_ACCEPTED
)
async def delete_feature(id: int, nametask: str, db: AsyncSession = Depends(get_db)):
    instance = instances.get(nametask)
    state = await crud.delete_feature(db=db, id=id)
    if state:
        await instance.restarttask()
    return
