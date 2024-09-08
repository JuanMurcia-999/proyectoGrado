from pysnmp.hlapi.asyncio.slim import Slim

async def slim_get(community, host, port, *VarBinds):
    with Slim(2) as slim:
        errorIndication, errorStatus, errorIndex, varBinds = await slim.get(
            community,
            host,
            port,
            *VarBinds
         )
        if errorIndication:
            return False 
        elif errorStatus:
            return False 
        else:
            return varBinds
