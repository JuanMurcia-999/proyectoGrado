from collections import deque
import asyncio
import crud




class HistoryFIFOQueue:
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
            print(self.queue)
    async def process_queue(self):
        while True:
            async with self.lock:
                if not self.queue:
                    self.task_running = False
                    return 
               
                item = self.queue.popleft()

            print(f"Número de elementos en la cola: {len(self.queue)}")
            success = await crud.add_history(item)

            if not success:
                
                async with self.lock:
                    self.queue.append(item)
            await asyncio.sleep(0.1)
