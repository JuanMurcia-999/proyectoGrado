from ..database import get_db
from sqlalchemy.future import select
from .. import models

Af = models.Administered_features

async def get_unique_times(id_agent):
    async for db in get_db():
        try:
            return (
                (
                    await db.execute(
                        select(Af.timer)
                        .filter(
                            Af.id_agent == id_agent,
                            Af.oid != "",
                        )
                        .distinct()
                    )
                )
                .scalars()
                .all()
            )
        except Exception as e:
            print(e)


async def get_features_oid(inter, id_agent):
    async for db in get_db():
        try:
            return (
                await db.execute(
                    select(Af.oid, Af.id_adminis).filter(
                        Af.timer == f"{inter}",
                        Af.id_agent == id_agent,
                        Af.oid != "",
                    )
                )
            ).all()
        except Exception:
            print("fallo en get_features")
