from collections import deque

import models
from database import SessionLocal


db = SessionLocal()


class HistoryFIFO:
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
            # print(f"Longitud:::  {len(self.cola)}")
            tarea = self.desencolar()
            # print(f"Procesando tarea: {tarea}")
            exito = await self.add_history(tarea)

            if exito:
                continue
                # print(f"Tarea completada con éxito.")
            else:
                print(f"Tarea falló. Reintentando...")
                await self.encolar(tarea)  # Volver a encolar la tarea para reintentar

    async def add_history(self, data):
        print(data)
        try:
              # Asegúrate de que cada tarea tenga su propia sesión
            db_history = models.History_features(
                id_agent=data.id_agent,
                id_adminis=data.id_adminis,
                value=data.value,
            )

            db.add(db_history)
            await db.commit()
            await db.refresh(db_history)
            return True
        except Exception:
            print('algo paso en la query')
            return False
        finally:
            pass
            # await db.close()
