from collections import deque
from Utilizables import sendmessage
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
import models, crud
from database import SessionLocal

# DATABASE_URL = "sqlite+aiosqlite:///GestorDB.sqlite"
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()


class AlarmsFIFO:
    def __init__(self):
        self.cola = deque()

    async def encolar(self, item):

        if self.esta_vacia():
            self.cola.append(item)
            await self.procesar_tareas()
        else:
            self.cola.append(item)

    def desencolar(self):
        if not self.esta_vacia():
            return self.cola.popleft()
        else:
            raise IndexError("Desencolar de una cola vacía")

    def esta_vacia(self):
        return len(self.cola) == 0

    async def procesar_tareas(self):
        while not self.esta_vacia():
            tarea = self.desencolar()
            exito = await self.check_alarm(tarea)
            if exito:
                if tarea.id_adminis < 100:
                    column = "id_adminis"
                else:
                    column = "id_sensor"
                query = await crud.get_administered_feature(db, column, tarea)
                message = f"ALARMA ACTIVA \n Sensor : {query.adminis_name} \n "
                sendmessage(message)
            else:
                pass

    async def check_alarm(self, data):
        try:
            if data.id_adminis < 100:
                column = "id_adminis"
            else:
                column = "id_sensor"

            response = await crud.get_alarms(db, column, data)
            if response:
                evaluation = f"{data.value} {response.operation} {response.value}"
            return eval(evaluation)
        except Exception:
            return False
