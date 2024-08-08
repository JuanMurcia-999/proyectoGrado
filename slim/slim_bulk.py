from pysnmp.hlapi.asyncio import *



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



