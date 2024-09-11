from collections import deque
from Utilizables.Register import Buffer
from Utilizables.BotTelegram import sendmessage
import schemas
import asyncio
import crud


overflow = 5

class HistoryFIFOQueue:
    def __init__(self):
        self.queue = deque()
        self.lock = asyncio.Lock()
        self.task_running = False
        self.countererror =0
        self.stateoverflow = False

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

            print(f"Número de elementos en la cola: {len(self.queue)}")
            if self.countererror < overflow:
                success = await crud.add_history(item)
            else:
                if not self.stateoverflow:
                    sendmessage('Desbordamiento de cola\nAlamacenando en buffer')
                    self.stateoverflow =True    
                Buffer(f'{item}\n')
                success = True
            if not success:
                async with self.lock:
                    self.queue.append(item)
                self.countererror +=1
            await asyncio.sleep(0.1)
