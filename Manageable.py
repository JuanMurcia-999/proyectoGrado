import asyncio
from Gestionables import AnchoBanda

class ManageableGeneral:
    def __init__(self, ip: str, name: str) -> None:
        self.name = name
        self.ip = ip
        self.tasks = {}  # Diccionario para almacenar tareas con identificadores

    async def Networktraffic(self, num_interface: str, intervalo: int, task_id: str) -> None:
        try:
            # Crear una tarea para ejecutar AnchoBanda y agregarla al diccionario de tareas
            task = asyncio.create_task(
                AnchoBanda(host=self.ip, Num_Interface=num_interface, intervalo=intervalo).run()
            )
            self.tasks[task_id] = task
            print(f'Nombre: {self.name}  | IP: {self.ip} | Interfaz: {num_interface}')
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



class ManageablePC(ManageableGeneral):
    async def saludar(self):
        print(f'estoy saludando con el equipo {self.name} que es PC')


class ManageableRT(ManageableGeneral):
    async def saludar(self):
        print(f'estoy saludando con el equipo {self.name} que es Router')

# async def main():
#     Camilo = ManageablePC('1.2.3.4.5.6.7', '192.168.20.25', 'Pc Camilo')
#     await Camilo.saludar()
#     await Camilo.description('12', 10, 'task_1')  # Agregar identificador de tarea
#     await Camilo.description('13', 10, 'task_2')  # Otra tarea con un identificador diferente
#     # Esperar un tiempo para demostrar la cancelación de tareas
#     await asyncio.sleep(15)  # Ajusta este tiempo según tus necesidades
#     Camilo.cancelar_tarea('task_1')  # Cancelar tarea específica
#     await Camilo.Iniciar()  # Verificar estado después de cancelar
#     Mateo = ManageablePC('1.2.3.4.5.6.7', '192.168.20.27', 'Pc Mateo')
#     await Mateo.saludar()
#     await Mateo.description('16', 10, 'task_3')
#     # Esperar un tiempo para demostrar la cancelación de tareas
#     await asyncio.sleep(15)
#     Mateo.cancelar_tarea('task_3')  # Cancelar tarea específica
#     await Mateo.Iniciar()  # Verificar estado después de cancelar
#     # Ejecutar todas las instancias simultáneamente
  

# if __name__ == "__main__":
#     asyncio.run(main())
