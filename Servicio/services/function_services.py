from ..database import get_db
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from .. import models


async def get_sensors_startup(id):
    async for db in get_db():
        try:
            return (
                (
                    await db.execute(
                        select(models.Active_default)
                        .options(joinedload(models.Active_default.features))
                        .filter(models.Active_default.id_agent == id)
                    )
                )
                .scalars()
                .all()
            )

        except Exception:
            print("fallo en get_sensors_startup")