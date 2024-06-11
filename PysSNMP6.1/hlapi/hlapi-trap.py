import asyncio
from pysnmp.hlapi.asyncio import *

async def run():
    errorIndication, errorStatus, errorIndex, varBinds = await sendNotification(
        SnmpEngine(),
        CommunityData('public'),
        UdpTransportTarget(('192.168.20.22', 162)),
        ContextData(),
        'trap',
        NotificationType(ObjectIdentity('IF-MIB', 'linkDown'))
        .addMibSource('C:/Users/User/Desktop/Proyecto de grado/snmp-mibs/')
        .addVarBinds(("1.3.6.1.2.1.1.1.0", OctetString("ayudaaaaaaa")))
        )
    
    
    print(errorIndication, errorStatus, errorIndex, varBinds)

asyncio.run(run())