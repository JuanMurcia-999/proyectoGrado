from collections import deque
import sys
import os


# Añade el directorio raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models


DATABASE_URL = "sqlite:///C:/Users/Juan Murcia/Desktop/Proyecto de grado/Desarrollo/Recolector/DataBases/productos.sqlite"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()



class HistoryFIFO:
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
            print(f'Longitud:::  {len(self.cola)}')
            tarea = self.desencolar()
            print(f"Procesando tarea: {tarea}")
            exito = self.add_history(tarea)
            if exito:
                print(f"Tarea {tarea} completada con éxito.")
            else:
                print(f"Tarea {tarea} falló. Reintentando...")
                self.encolar(tarea)  # Volver a encolar la tarea para reintentar

    def add_history(self, data):
        try:    
            db = SessionLocal()  # Asegúrate de que cada tarea tenga su propia sesión
            db_history = models.History_features(
                id_agent=data.id_agent,
                id_adminis=data.id_adminis,
                value=str(data.value)
            )

            db.add(db_history)
            db.commit()
            db.refresh(db_history)
            db.close()
            return True
        except Exception:
            return False






