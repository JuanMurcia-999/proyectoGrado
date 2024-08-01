import asyncio
from pysnmp.hlapi.asyncio import *

async def run():
    errorIndication, errorStatus, errorIndex, varBinds = await setCmd(
        SnmpEngine(),
        CommunityData('public'),
        UdpTransportTarget(('192.168.20.25', 161)),
        ContextData(),
        ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName', 0), 'DESKTOP-930A5GD')
        
    )
    print(errorIndication, errorStatus, errorIndex, varBinds)

asyncio.run(run())