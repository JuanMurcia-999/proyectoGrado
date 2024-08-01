import asyncio
from pysnmp.hlapi.asyncio.slim import Slim
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
   
async def run():
    with Slim() as slim:
        errorIndication, errorStatus, errorIndex, varBinds = await slim.next(
            'public',
            '192.168.20.22',
            161,
            ObjectType(ObjectIdentity(".1.3.6.1.2.1.1.1.0"))
        )
                
        if errorIndication:
            print(errorIndication)
        elif errorStatus:
            print(
                "{} at {}".format(
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex) - 1][0] or "?",
                )
            )
        else:
            for varBind in varBinds:
                print(" = ".join([x.prettyPrint() for x in varBind]))
        


asyncio.run(run())
        
        