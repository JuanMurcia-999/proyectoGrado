from sqlalchemy.ext.asyncio import AsyncSession
from ..schema import alarms_schemas as schema
from sqlalchemy.future import select
from .. import models


Al = models.Alarms

async def get_alarm(db: AsyncSession, id_agent):
    try:
        result = await db.execute(select(Al).filter(Al.id_agent == id_agent))
        return result.scalars().all()
    except Exception:
        return False


async def delete_alarm(db: AsyncSession, id_alarm):
    db_alarm = await db.execute(select(Al).filter(Al.id_alarm == id_alarm))

    db_alarm_instance = db_alarm.scalar_one_or_none()

    if db_alarm_instance:
        await db.delete(db_alarm_instance)
        await db.commit()
        return True
    else:
        return False


async def add_alarm(db: AsyncSession, alarm: schema.newAlarm):
    try:
        addalarm = Al(
            id_agent=alarm.id_agent,
            id_adminis=alarm.id_adminis,
            id_sensor=alarm.id_sensor,
            operation=alarm.operation,
            value=alarm.value,
        )

        db.add(addalarm)
        await db.commit()
        await db.refresh(addalarm)

        return True
    except Exception:
        return False
