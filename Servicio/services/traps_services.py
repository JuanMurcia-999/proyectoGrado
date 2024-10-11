from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .. import models


Ts = models.Traps

async def get_all_traps(db: AsyncSession):
    result = await db.execute(select(Ts))
    return result.scalars().all()


async def get_trap_message(value, db: AsyncSession):
    result = await db.execute(select(Ts.message).filter(Ts.id_alarm == value))
    valor = result.scalar_one_or_none()
    return valor