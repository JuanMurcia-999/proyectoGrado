from collections import deque
import sys
import os


# Añade el directorio raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from BotTelegram import sendmessage
import models


DATABASE_URL = "sqlite:///productos.sqlite"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()


class AlarmsFIFO:
    def __init__(self):
        self.cola = deque()

    def encolar(self, item):

        if self.esta_vacia():
            self.cola.append(item)
            self.procesar_tareas()
        else:
            self.cola.append(item)

    def desencolar(self):
        if not self.esta_vacia():
            return self.cola.popleft()
        else:
            raise IndexError("Desencolar de una cola vacía")

    def esta_vacia(self):
        return len(self.cola) == 0

    def procesar_tareas(self):
        while not self.esta_vacia():
            tarea = self.desencolar()
            exito = self.check_alarm(tarea)
            if exito:
                if tarea.id_adminis < 100:
                    column = "id_adminis"
                else:
                    column = "id_sensor"
                query = (
                    db.query(models.Administered_features)
                    .filter(
                        getattr(models.Administered_features, column)
                        == tarea.id_adminis
                    )
                    .first()
                )
                message = f"ALARMA ACTIVA \n Sensor : {query.adminis_name} \n "
                sendmessage(message)
            else:
                print(f"Alarm sin cumplir")

    def check_alarm(self, data):
        try:
            if data.id_adminis < 100:
                column = "id_adminis"
            else:
                column = "id_sensor"

            response = (
                db.query(models.Alarms)
                .join(
                    models.Administered_features,
                    models.Alarms.id_adminis == models.Administered_features.id_adminis,
                )
                .filter(
                    and_(
                        getattr(models.Administered_features, column)
                        == data.id_adminis,
                        models.Administered_features.id_agent == data.id_agent,
                    )
                )
                .first()
            )
            if response:
                evaluation = f"{data.value} {response.operation} {response.value}"
            return eval(evaluation)
        except Exception:
            return False
