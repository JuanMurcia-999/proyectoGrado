import asyncio
from Gestionables import AnchoBanda,Processes, ping
from DataBases.taskoid import sensorOID
from DataBases import schemas



class ManageableGeneral:
    def __init__(self, ip: str, name: str,id:int) -> None:
        self.name = name
        self.ip = ip
        self.id = id
        self.state = False
    
    async def Networktraffic(self, params,nametask,cola,alarms) -> None:
        taskname = nametask+params['num_interface']
        print(taskname)
        try:
            # Crear una tarea para ejecutar AnchoBanda y agregarla al diccionario de tareas
            Config = {"ip":self.ip, "Num_Interface": params['num_interface'], "intervalo":params['timer'],
                      "id_adminis":params['id_adminis'],"id":self.id, "history":cola,"alarms":alarms}
            Config = schemas.ConfigAnchoBanda(**Config)
            task = asyncio.create_task(
                AnchoBanda(Config=Config).run()
            )
            if hasattr(self, 'tasks'):
                self.tasks[taskname] = task  
            print(f'Nombre: {self.name}  | IP: {self.ip} | Interfaz: {params['num_interface']}')
        except Exception as e:
            print(f'Error en la descripción: {e}')
        
    async def state_device(self):
        #self.state = await ping(self.ip)
        
        #print(f'agente {self.name} Activo: {self.state}')
        return True






class ManageablePC(ManageableGeneral):

    def __init__(self, ip: str, name: str,id:int) -> None:
        super().__init__(ip, name,id)
        self.tasks = {}
        self.taskoid=[]
        self.id= id
        self.instanceoid = sensorOID

    async def saludar(self):
        print(f'estoy saludando con el equipo {self.name} que es PC')

    async def NumProccesses(self, params, task_id,cola,alarms):
        try:
            Config = {"ip":self.ip, "timer":params['timer'],"id_adminis":params['id_adminis'],"id":self.id, "history":cola, "alarms":alarms}
            Config = schemas.ConfigProcesses(**Config)
            task = asyncio.create_task(
                Processes(Config=Config).TaskNumProcesses()
            )
            if self.tasks is not None:
                self.tasks[task_id] = task
            print(self.tasks)
        except Exception as e:
              print(f'Error en la descripción: {e}')
 
    async def MemorySize(self, params, task_id,cola,alarms):
        try:
            Config = {"ip":self.ip, "timer":params['timer'],"id_adminis":params['id_adminis'],"id":self.id, "history":cola, "alarms":alarms}
            Config = schemas.ConfigProcesses(**Config)
            task = asyncio.create_task(
                Processes(Config=Config).TaskMemorySize()
            )
            if self.tasks is not None:
                self.tasks[task_id] = task
            print(self.tasks)
        except Exception as e:
              print(f'Error en la descripción: {e}')

    async def restarttask(self):
        await self.instanceoid.CreatorTask()

    async def task_oid(self):
         self.instanceoid = sensorOID(self.ip, self.id, self.state_device)
         await self.instanceoid.CreatorTask()




    async def Iniciar(self):
        # Esperar a que todas las tareas en el diccionario se completen
        if self.tasks:
      
            await asyncio.gather(*self.tasks.values())

    async def cancelar_tarea(self, task_id: str):
        # Cancelar una tarea específica por su identificador
        if task_id in self.tasks:
            task = self.tasks.pop(task_id)
            task.cancel()
            # Esperar a que la tarea sea cancelada
            await self._esperar_cancelacion(task)


    async def _esperar_cancelacion(self, task):
        try:
            await task
        except asyncio.CancelledError:
            # La tarea fue cancelada, capturamos la excepción
            print(f'Tarea cancelada: {task}')




class ManageableRT(ManageableGeneral):
    def __init__(self, ip: str, name: str , id:int) -> None:
        super().__init__(ip, name)
        self.tasks = {}
        self.id= id
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
