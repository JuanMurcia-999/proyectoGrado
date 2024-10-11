from ..schema import features_schemas as schema
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select

from .. import models


Af = models.Administered_features


# Query para obtener todas las caracteristicas que son monitoreadas
async def get_all_features(db: AsyncSession):
    result = await db.execute(select(Af).options(joinedload(Af.agent)))
    return result.scalars().all()


# Query para obtener todas las caracteristicas segun agente
async def get_all_features_agent(db: AsyncSession, value):
    result = await db.execute(
        select(Af).filter(Af.id_agent == value).options(joinedload(Af.agent))
    )
    return result.scalars().all()


# Agregar una nueva feature a monitorizar
async def new_feature(db: AsyncSession, feature: schema.new_features):
    try:

        db_feature = Af(
            # id_adminis=feature.id_adminis,
            id_sensor=feature.id_sensor,
            id_agent=feature.id_agent,
            oid=feature.oid,
            adminis_name=feature.adminis_name,
            timer=feature.timer,
        )

        db.add(db_feature)
        await db.commit()
        await db.refresh(db_feature)
        return True
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sensor ya activo"
        )


# Query para eleiminacion de features
async def delete_feature(db: AsyncSession, id):
    try:
        # Ejecutar la consulta y esperar el resultado
        result = await db.execute(select(Af).filter(Af.id_adminis == id))
        db_feature = result.scalar_one_or_none()

        if db_feature:
            await db.delete(db_feature)
            await db.commit()
            return True
    except Exception:
        return False
