import asyncio


async def Get_SNMP(num):
    await asyncio.sleep(num)
    return num

async def Getcosas(num):
    while True:
        await asyncio.sleep(num)
        print('ejecutando tarea independiente')


async def main():

    task7 = asyncio.create_task(Getcosas(1))
    async with asyncio.TaskGroup() as tg :
        task1=  tg.create_task(Get_SNMP(1))
        task2=  tg.create_task(Get_SNMP(2))
        task3=  tg.create_task(Get_SNMP(3))
        task4=  tg.create_task(Get_SNMP(4))
        task5=  tg.create_task(Get_SNMP(5))
        task6=  tg.create_task(Get_SNMP(6))

       
    print(f"Both tasks have completed now: {task1.result(), task2.result(),task3.result(), task4.result(),task5.result(), task6.result()}")

    while True:
        await asyncio.sleep(0.001)
    


asyncio.run(main())