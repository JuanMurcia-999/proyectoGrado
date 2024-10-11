from ..database import get_db
from sqlalchemy.future import select
from sqlalchemy import  and_, func
from ..schema.history_schemas import filterHistory
from .. import models


Hf = models.History_features

async def get_A_cpu(date):
    async for db in get_db():
        try:
            return (
                (
                    await db.execute(
                        select(Hf.id_adminis)
                        .filter(Hf.id_adminis.like(f"{date}%"))
                        .distinct()
                    )
                )
                .scalars()
                .all()
            )
        except Exception:
            print("fallo get_A_cpu")


async def get_B_cpu(filter: filterHistory, id):

    async for db in get_db():
        try:
            valor = (
                await db.execute(
                    select(Hf.value, Hf.time, Hf.date)
                    .filter(
                        and_(Hf.id_agent == filter.id_agent, Hf.id_adminis == id),
                        func.DATE(Hf.date) == func.DATE(f"{filter.datebase}"),
                        and_(
                            func.TIME(Hf.time)
                            >= func.TIME(f"{filter.timebase}", f"{filter.timerange}"),
                            func.TIME(Hf.time) <= func.TIME(f"{filter.offset}"),
                        ),
                    )
                    .limit(filter.limit)
                )
            ).all()
            return valor
        except Exception:
            print("fallo get_B_cpu")


async def get_B_network(filter: filterHistory, ids):
    async for db in get_db():
        try:
            return (
                await db.execute(
                    select(Hf.value, Hf.time, Hf.date)
                    .filter(
                        and_(
                            Hf.id_agent == filter.id_agent,
                            Hf.id_adminis.in_([ids["In"], ids["Out"]]),
                            func.DATE(Hf.date) == func.DATE(f"{filter.datebase}"),
                            and_(
                                func.TIME(Hf.time)
                                >= func.TIME(
                                    f"{filter.timebase}", f"{filter.timerange}"
                                ),
                                func.TIME(Hf.time) <= func.TIME(f"{filter.offset}"),
                            ),
                        )
                    )
                    .limit(filter.limit)
                )
            ).all()
        except Exception:
            print("fallo get_B_network")