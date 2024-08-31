import asyncio
from collections import deque
import random
import models
from database import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
# db=SessionLocal()

class AsyncFIFOQueue:
    def __init__(self,Session:AsyncSession):
        self.queue = deque()
        self.lock = asyncio.Lock()
        self.task_running = False
        self.db=Session

    async def add(self, item):
        async with self.lock:
            self.queue.append(item)
            if not self.task_running:
                self.task_running = True
                asyncio.create_task(self.process_queue())

    async def process_queue(self):
        while True:
            async with self.lock:
                if not self.queue:
                    self.task_running = False
                    return  # Salir si la cola está vacía
            
                # Obtener el primer elemento de la cola
                item = self.queue.popleft()
            
            print(f"Número de elementos en la cola: {len(self.queue)}")
            success = await self.execute_task(item)
            if not success:
                # Si la tarea no se cumple, reintegrar el elemento a la cola
                async with self.lock:
                    self.queue.append(item)
            else:
                pass
                # print(f"Tarea completada con éxito para el elemento: {item}")

            # Esperar un breve momento antes de continuar
            await asyncio.sleep(0.1)

    async def execute_task(self, data):
        try:
              # Asegúrate de que cada tarea tenga su propia sesión
            db_history = models.History_features(
                id_agent=data.id_agent,
                id_adminis=data.id_adminis,
                value=data.value,
            )

            self.db.add(db_history)
            await self.db.commit()
            await self.db.refresh(db_history)
            return True
        except Exception:
            print('algo paso en la query')
            return False
        finally:
            pass
            # await self.db.close()

# async def add_tasks_continuously(fifo_queue):
#     task_number = 1
#     while True:
#         await fifo_queue.add(f"Tarea {task_number}")
#         task_number += 1
#         await asyncio.sleep(random.uniform(0.1, 0.5))  # Esperar un tiempo aleatorio antes de agregar la siguiente tarea

# async def main():
#     fifo_queue = AsyncFIFOQueue()
    
#     # Iniciar la tarea que agrega elementos a la cola continuamente
#     asyncio.create_task(add_tasks_continuously(fifo_queue))

#     await asyncio.sleep(30)  # Dejar que las tareas se procesen

# # Ejecutar el programa
# asyncio.run(main())
