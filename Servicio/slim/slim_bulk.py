from pysnmp.hlapi.asyncio import *
from pysnmp.hlapi.asyncio.slim import Slim


async def get_bulk(community, host, port, nonRepeaters, maxRepetitions, *varBinds):
    iterator = bulkCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((host, port)),
        ContextData(),
        nonRepeaters, maxRepetitions,
        *varBinds,
        lookupMib=False
    )
    
    errorIndication, errorStatus, errorIndex, varBinds = await iterator
    
    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        return varBinds



async def slim_bulk(community, host, port, nonRepeaters, maxRepetitions, *varBinds):
    with Slim(2) as slim:
        errorIndication, errorStatus, errorIndex, varBinds = await slim.bulk(
            community,
            host,
            port,
            nonRepeaters, maxRepetitions,
            *varBinds,
            #.addMibSource('C:/Users/User/Desktop/Proyecto de grado/Librerias/PySNMP6.1/mibs-compiler/') 
         )
    
        if errorIndication:
            
            return
        elif errorStatus:

            return
        else:
            return varBinds
        

