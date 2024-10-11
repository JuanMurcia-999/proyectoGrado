from sqlalchemy.ext.asyncio import AsyncSession
from ..schema import history_schemas as schema
from sqlalchemy.future import select
from sqlalchemy import  and_, func

from  .. import models
Hf = models.History_features
Af = models.Administered_features

Faile = {
    "data": {
        "datagrafic": [
            {
                "name": "Sin datos",
                "values": [],
                "date": [],
                "time": [],
                "stadistics": {
                    "min": 0,
                    "max": 0,
                    "avg": 0,
                },
            }
        ],
    },
}




async def get_history_Network(db: AsyncSession, filter: schema.getHistory):

    result_in = await db.execute(
        select(Hf.value, Hf.date)
        .filter(
            Hf.id_adminis == 1001,
            Hf.id_agent == filter.id_agent,
        )
        .order_by(Hf.id_register.desc())
    )
    IN = result_in.fetchall()

    result_out = await db.execute(
        select(Hf.value, Hf.date)
        .filter(
            Hf.id_adminis == 1002,
            Hf.id_agent == filter.id_agent,
        )
        .order_by(Hf.id_register.desc())
    )
    OUT = result_out.fetchall()

    valuesIN = [item[0] for item in IN]
    valuesOUT = [item[0] for item in OUT]
    date = [item[1].strftime("%Y-%m-%d") for item in IN]

    return {"value": {"valuesIN": valuesIN, "valuesOUT": valuesOUT}, "created_at": date}


async def get_history_filter(db: AsyncSession, filter: schema.filterHistory):
    if filter.id_sensor is None:
        condition = filter.id_adminis
        column = "id_adminis"
    else:
        condition = filter.id_sensor
        column = "id_sensor"
    print(filter)
    try:
        result = await db.execute(
            select(Hf.value, Hf.time, Hf.date)
            .filter(
                and_(
                    Hf.id_agent == filter.id_agent,
                    Hf.id_adminis == condition,
                    func.DATE(Hf.date) == func.DATE(f"{filter.datebase}"),
                    and_(
                        func.TIME(Hf.time)
                        >= func.TIME(f"{filter.timebase}", f"{filter.timerange}"),
                        func.TIME(Hf.time) <= func.TIME(f"{filter.offset}"),
                    ),
                )
            )
            .order_by(Hf.date.asc())
            .limit(filter.limit)
        )
        response = result.fetchall()
        name_result = await db.execute(
            select(Af.adminis_name).filter(getattr(Af, column) == condition)
        )
        namesensor = name_result.first().adminis_name
        if response != [] and name_result != None:

            values = [item.value for item in response]
            # print(values)
            time = [item.time for item in response]
            # print(time)
            date = [item.date for item in response]
            # print(date)
            minimum = min(values)
            maximus = max(values)
            average = sum(values) / len(values)

            return {
                "data": {
                    "datagrafic": [
                        {
                            "name": namesensor,
                            "values": values,
                            "date": date,
                            "time": time,
                            "stadistics": {
                                "min": minimum,
                                "max": maximus,
                                "avg": average,
                            },
                        }
                    ],
                },
            }
        else:
            return Faile
    except Exception as e:
        return Faile
