import asyncio
from pysnmp.hlapi.asyncio.slim import Slim
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType

async def run():
    with Slim() as slim:
        errorIndication, errorStatus, errorIndex, varBinds = await slim.bulk(
            'public',
            '192.168.20.25',
            161,0,2,
            ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName', 0))
            #.addMibSource('C:/Users/User/Desktop/Proyecto de grado/snmp-mibs/')
            #.addMibSource('C:/Users/User/Desktop/Proyecto de grado/Librerias/PySNMP6.1/mibs-compiler/')
        )
        if errorIndication:
            print(errorIndication)
        
        else:
            for varBind in varBinds:
                print(" = ".join([x.prettyPrint() for x in varBind]))
asyncio.run(run())  