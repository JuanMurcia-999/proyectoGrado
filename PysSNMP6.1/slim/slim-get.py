import asyncio
from pysnmp.hlapi.asyncio.slim import Slim
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
import pdb

async def run():
    
    
    with Slim(2) as slim:
        
        errorIndication, errorStatus, errorIndex, varBinds = await slim.get(
            "public",
            "192.168.20.25",
            161,
            ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysName', 0))
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
            for varBind in varBinds:
                #print(varBind)
                print(" = ".join([x.prettyPrint() for x in varBind]))
            


