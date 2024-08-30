from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_, and_, func
import models
import schemas

# Configuración de la base de datos
DATABASE_URL = "sqlite:///productos.sqlite"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

Fail = {
        "data": {
            "datagrafic": [
                  {
                        "name": 'Sin datos',
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



Hf = models.History_features

class Abtraciones:

    response_json = {
        "data": {
            "datagrafic": [],
        },
    }
    names = {}
    base = response_json["data"]["datagrafic"]

    async def CPU(self, dato, filter: schemas.filterHistory):
        try:
            self.base.clear()

            A = (
                db.query(Hf.id_adminis)
                .filter(Hf.id_adminis.like(f"{dato}%"))
                .distinct()
                .all()
            )

            id_adminis = [id[0] for id in A]
            self.names[id_adminis[0]] = "General"
            for id in range(1, len(id_adminis)):
                self.names[id_adminis[id]] = f"core{id}"

            for id, name in self.names.items():
                B = (
                    db.query(Hf.value, Hf.time, Hf.date)
                    .filter(
                        and_(
                            Hf.id_agent == filter.id_agent,
                            Hf.id_adminis == id,
                            Hf.date >= func.date(filter.datebase, filter.daterange),
                            Hf.time >= func.time("now", filter.timerange),
                        )
                    )
                    .order_by(Hf.date.asc())
                    .limit(filter.limit)
                    .offset(filter.offset)
                    .all()
                )

                values = [item.value for item in B]
                time = [item.time.strftime("%H:%M:%S") for item in B]
                date = [item.date.strftime("%Y-%m-%d") for item in B]

                self.base.append(
                    {
                        "name": name,
                        "values": values,
                        "date": date,
                        "time": time,
                        "stadistics": {
                            "min": min(values),
                            "max": max(values),
                            "avg": sum(values) / len(values),
                        },
                    }
                )
        except Exception:
            return Fail
        finally:
            return self.response_json

    async def NETWORK(self, filter: schemas.filterHistory):
        try:
            self.base.clear()
            id_adminis = int(str(filter.id_sensor)[:-1])
            ids = {
                name: int(f"{id_adminis}{item}")
                for name, item in zip(("In", "Out"), (0, 1))
            }

            B = (
                db.query(Hf.value, Hf.time, Hf.date, Hf.id_adminis)
                .filter(
                    and_(
                        Hf.id_agent == filter.id_agent,
                        Hf.id_adminis.in_([ids["In"], ids["Out"]]),
                        Hf.date >= func.date(filter.datebase, filter.daterange),
                        Hf.time >= func.time("now", filter.timerange),
                    )
                )
                .order_by(Hf.date.asc())
                .limit(filter.limit)
                .offset(filter.offset)
                .all()
            )

            In = [item for item in B[::2]]
            Out = [item for item in B[1::2]]

            for id, data in zip(ids, (In, Out)):
                values = [item.value for item in data]
                time = [item.time.strftime("%H:%M:%S") for item in data]
                date = [item.date.strftime("%Y-%m-%d") for item in data]

                self.base.append(
                    {
                        "name": id,
                        "values": values,
                        "date": date,
                        "time": time,
                        "stadistics": {
                            "min": min(values),
                            "max": max(values),
                            "avg": sum(values) / len(values),
                        },
                    }
                )
        except Exception:
           return Fail
        finally:
            return self.response_json
