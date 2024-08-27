import subprocess
import asyncio


async def ping(ip:str):

    p = subprocess.Popen(
        ["ping", "-n", "2", "-w", "2", ip],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    p.wait()
    return True if p.poll() == 0 else False


# async def main():
#     state = await ping('192.168.20.42')
#     print(state)
 


# asyncio.run(main())
