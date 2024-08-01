import asyncio
from pysnmp.hlapi.asyncio.slim import Slim
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
import pdb

async def slim_get(community, host, port, *VarBinds):
    
    
    with Slim(2) as slim:
        
        errorIndication, errorStatus, errorIndex, varBinds = await slim.get(
            community,
            host,
            port,
            *VarBinds
            #.addMibSource('C:/Users/User/Desktop/Proyecto de grado/Librerias/PySNMP6.1/mibs-compiler/')
            
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
            return varBinds
