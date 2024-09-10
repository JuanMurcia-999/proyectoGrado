from Utilizables.BotTelegram import sendmessage
from collections import deque
import asyncio
import crud




class AlarmFIFOQueue:
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
                    return 
       
                item = self.queue.popleft()
            
            print(f"Número en Alrmas: {len(self.queue)}")
            success = await self.execute_task(item)
            if success:
                if item.id_adminis < 100:
                    column = "id_adminis"
                else:
                    column = "id_sensor"
                query = await crud.get_administered_feature(column, item)
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

            response = await crud.get_alarms(column, data)
            if response:
                evaluation = f"{data.value} {response.operation} {response.value}"
                return eval(evaluation)
        except Exception:
            return False

