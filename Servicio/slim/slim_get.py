from pysnmp.hlapi.asyncio.slim import Slim

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
            return
        elif errorStatus:
            return
        else:
            return varBinds




