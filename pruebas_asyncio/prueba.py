import asyncio

async def task1():
    print("Tarea 1 empieza")
    await asyncio.sleep(2)
    print("Tarea 1 termina")

async def task2():
    print("Tarea 2 empieza")
    await asyncio.sleep(1)
    print("Tarea 2 termina")

async def task3():
    print("Tarea 3 empieza")
    await asyncio.sleep(3)
    print("Tarea 3 termina")

async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(task1())
        tg.create_task(task2())
        tg.create_task(task3())
    
    print("Todas las tareas han terminado")

# Ejecuta la función main
asyncio.run(main())
