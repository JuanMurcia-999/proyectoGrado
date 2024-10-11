from ..schema import agents_schemas as schema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException,status
from .. import models


Ag = models.Agents


async def get_all_agent(db: AsyncSession):
    result = await db.execute(select(Ag).options(selectinload(Ag.type)))
    return result.scalars().all()


async def create_agent(db: AsyncSession, agent: schema.CreateAgent):
    try:
        db_agent = Ag(
            ag_name=agent.ag_name,
            ip_address=agent.ip_address,
            ag_type=agent.ag_type,
        )

        db.add(db_agent)
        await db.commit()
        await db.refresh(db_agent)
        return db_agent.id_agent
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="El agente ya existe"
        )

async def delete_agent(db: AsyncSession, field, value):
    try:
        result = await db.execute(select(Ag).filter(getattr(Ag, field) == value))
        db_agent = result.scalars().first()
        if db_agent:
            await db.delete(db_agent)
            await db.commit()
            return db_agent
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El agente no existe",
        )

