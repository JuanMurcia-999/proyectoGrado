import asyncio

from services.get_all_features import Get_all_features
from slimsnmp.get import get_snmp



async def main():
    await asyncio.sleep(5)
    print("recolector iniciado")


if __name__ == "__main__":
    asyncio.run(main())


