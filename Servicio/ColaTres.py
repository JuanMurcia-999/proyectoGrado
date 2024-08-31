import asyncio
from collections import deque
import random
import models
from database import SessionLocal
import crud
from Utilizables.BotTelegram import sendmessage

db=SessionLocal()

class AsyncFIFOQueue:
    def __init__(self):
        self.queue = deque()
        self.lock = asyncio.Lock()
        self.task_running = False

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
            
            print(f"Número en Alrmas: {len(self.queue)}")
            success = await self.execute_task(item)
            if not success:
                # Si la tarea no se cumple, reintegrar el elemento a la cola
                async with self.lock:
                    self.queue.append(item)
            else:
                if item.id_adminis < 100:
                    column = "id_adminis"
                else:
                    column = "id_sensor"
                query = await crud.get_administered_feature(db, column, item)
                message = f"ALARMA ACTIVA \n Sensor : {query.adminis_name} \n "
                sendmessage(message)

            # Esperar un breve momento antes de continuar
            await asyncio.sleep(0.1)

    async def execute_task(self, data):
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
