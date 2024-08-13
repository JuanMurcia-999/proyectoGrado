import asyncio
from Gestionables import AnchoBanda,Processes
from slim.slim_get import slim_get
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType





class ManageableGeneral:
    def __init__(self, ip: str, name: str) -> None:
        self.name = name
        self.ip = ip
    
    async def Networktraffic(self, num_interface: str, intervalo: int, task_id: str) -> None:
        try:
            # Crear una tarea para ejecutar AnchoBanda y agregarla al diccionario de tareas
            task = asyncio.create_task(
                AnchoBanda(host=self.ip, Num_Interface=num_interface, intervalo=intervalo).run()
            )
            if hasattr(self, 'tasks'):
                self.tasks[task_id] = task  
            print(f'Nombre: {self.name}  | IP: {self.ip} | Interfaz: {num_interface}')
        except Exception as e:
            print(f'Error en la descripción: {e}')





class ManageablePC(ManageableGeneral):

    def __init__(self, ip: str, name: str) -> None:
        super().__init__(ip, name)
        self.tasks = {}

    async def saludar(self):
        print(f'estoy saludando con el equipo {self.name} que es PC')

    async def NumProccesses(self, timer, task_id):
        try:
            task = asyncio.create_task(
                Processes(ip=self.ip, timer=timer).TaskNumProcesses()
            )
            if self.tasks is not None:
                self.tasks[task_id] = task
        except Exception as e:
              print(f'Error en la descripción: {e}')

    async def MemorySize(self, timer, task_id):
        try:
            task = asyncio.create_task(
                Processes(ip=self.ip, timer=timer).TaskMemorySize()
            )
            if self.tasks is not None:
                self.tasks[task_id] = task
        except Exception as e:
              print(f'Error en la descripción: {e}')




    async def Iniciar(self):
        # Esperar a que todas las tareas en el diccionario se completen
        if self.tasks:
            print(self.tasks)
            await asyncio.gather(*self.tasks.values())

    def cancelar_tarea(self, task_id: str):
        # Cancelar una tarea específica por su identificador
        if task_id in self.tasks:
            task = self.tasks.pop(task_id)
            task.cancel()
            # Esperar a que la tarea sea cancelada
            asyncio.create_task(self._esperar_cancelacion(task))

    async def _esperar_cancelacion(self, task):
        try:
            await task
        except asyncio.CancelledError:
            # La tarea fue cancelada, capturamos la excepción
            print(f'Tarea cancelada: {task}')




class ManageableRT(ManageableGeneral):
    def __init__(self, ip: str, name: str) -> None:
        super().__init__(ip, name)
        self.tasks = {}
    async def saludar(self):
        print(f'estoy saludando con el equipo {self.name} que es Router')

    async def Iniciar(self):
        # Esperar a que todas las tareas en el diccionario se completen
        if self.tasks:
            print(self.tasks)
            await asyncio.gather(*self.tasks.values())

    def cancelar_tarea(self, task_id: str):
        # Cancelar una tarea específica por su identificador
        if task_id in self.tasks:
            task = self.tasks.pop(task_id)
            task.cancel()
            # Esperar a que la tarea sea cancelada
            asyncio.create_task(self._esperar_cancelacion(task))

    async def _esperar_cancelacion(self, task):
        try:
            await task
        except asyncio.CancelledError:
            # La tarea fue cancelada, capturamos la excepción
            print(f'Tarea cancelada: {task}')




# async def main():
#     pc = ManageablePC(ip="192.168.20.25", name="Camilo")
#     await pc.Networktraffic(num_interface="12", intervalo=10, task_id="task1")
#     #await pc.NumProccesses(timer=5, task_id="task2")
#     #await pc.Iniciar()

#     # Para cancelar la tarea después de un tiempo
#     await asyncio.sleep(30)
#     pc.cancelar_tarea("task1")

# asyncio.run(main())