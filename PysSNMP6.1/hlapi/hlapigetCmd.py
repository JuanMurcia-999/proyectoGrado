from pysnmp.hlapi.asyncio import *

async def SNMPget(agent,oid):
    errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
        SnmpEngine(),
        CommunityData('public', mpModel=1),
        UdpTransportTarget((agent, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
        
    )
    
    for obj in varBinds:
        oid = obj[0].prettyPrint()
        value = obj[1].prettyPrint()
        print(f'{oid} = {value}')

    return[errorIndication, errorStatus, errorIndex, varBinds]



