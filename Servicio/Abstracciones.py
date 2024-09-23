import models
import schemas
import crud



Fail = {
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
            A = await crud.get_A_cpu(dato)

            id_adminis = [id for id in A]
            self.names[id_adminis[0]] = "General"
            for id in range(1, len(id_adminis)):
                self.names[id_adminis[id]] = f"Core{id}"
            print(self.names)
            for id, name in self.names.items():
                
                B = await crud.get_B_cpu(filter,id)

                values = [item.value for item in B]
                # time = [item.time.strftime("%H:%M:%S") for item in B]
                # date = [item.date.strftime("%Y-%m-%d") for item in B]
                time = [item.time for item in B]
                date = [item.date for item in B]
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
            self.names.clear()
            return self.response_json

    async def NETWORK(self, filter: schemas.filterHistory):
        try:
            self.base.clear()
            id_adminis = int(str(filter.id_sensor)[:-1])
            ids = {
                name: int(f"{id_adminis}{item}")
                for name, item in zip(("In", "Out"), (0, 1))
            }

            B = await crud.get_B_network(filter,ids)

            In = [item for item in B[::2]]
            Out = [item for item in B[1::2]]

            for id, data in zip(ids, (In, Out)):
                values = [item.value for item in data]
                time = [item.time for item in data]
                date = [item.date for item in data]
                # time = [item.time.strftime("%H:%M:%S") for item in data]
                # date = [item.date.strftime("%Y-%m-%d") for item in data]
                

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
            return self.response_json
        except Exception:
            print("fallo NETWORK")
            return Fail
        finally:
            self.names.clear()
