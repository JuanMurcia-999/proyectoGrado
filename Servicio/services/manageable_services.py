from ..schema import manageable_schemas as schema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, func
from fastapi import HTTPException,status
from .. import models
import json

Ad = models.Active_default
Df = models.Default_features
Af = models.Administered_features


async def get_default_features_agent(db: AsyncSession, id, type):
    if type == 4:
        types = [4, 2]
    else:
        types = [type]
    result = await db.execute(
        select(Df.fe_name, Df.id_feature)
        .outerjoin(
            Ad,
            and_(
                Df.id_feature == Ad.id_feature,
                Ad.id_agent == id,
            ),
        )
        .filter(
            and_(
                Ad.id_feature.is_(None),
                Df.id_type.in_([1, *types]),
                Df.id_feature != 100,
            )
        )
    )

    return result.all()


async def get_active_default(db: AsyncSession, id, type):
    if type == 4:
        types = [4, 2]
    else:
        types = [type]
    result = await db.execute(
        select(Df.fe_name, Df.id_feature)
        .join(
            Ad,
            Df.id_feature == Ad.id_feature,
        )
        .filter(
            and_(
                Ad.id_agent == id,
                Df.id_type.in_([1, *types]),
                Ad.id_feature != 100,
            )
        )
    )

    return result.all()


async def add_active_default(db: AsyncSession, dates: schema.Manageable):

    try:
        result = await db.execute(
            select(Ad).filter(
                and_(Ad.id_agent == dates.id_agent, Ad.id_feature == dates.id_feature)
            )
        )
        if result:
            params_json = json.dumps(dates.params)
            addactive = Ad(
                id_feature=dates.id_feature, id_agent=dates.id_agent, params=params_json
            )

            db.add(addactive)
            await db.commit()
            await db.refresh(addactive)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Sensor ya activo"
        )


async def delete_feature_two(db: AsyncSession, name, id):
    try:
        result = await db.execute(
            select(Af).filter(
                and_(
                    Af.adminis_name.like(f"{name}%"),
                    Af.id_agent == id,
                )
            )
        )

        db_feature = result.scalars().all()  #

        if db_feature:
            for feature in db_feature:
                await db.delete(feature)
            await db.commit()

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sensor no activo"
        )


async def delete_active_default(db: AsyncSession, dates: schema.Manageable):
    try:
        result = await db.execute(
            select(Ad).filter(
                and_(
                    Ad.id_feature == dates.id_feature,
                    Ad.id_agent == dates.id_agent,
                )
            )
        )
        db_active = result.scalars().first()

        if db_active:
            await db.delete(db_active)
            await db.commit()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sensor no activo"
        )


