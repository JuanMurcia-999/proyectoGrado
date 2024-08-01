from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
from slim.slim_bulk import get_bulk
from slim.slim_get import slim_get
import asyncio
import json



async def create_object_types(base_oid, indices):
    OIDs=[ObjectType(ObjectIdentity(f'{base_oid}.{i}')) for i in indices]
    return OIDs

      
async def interfaceTable(community,host):
    #community='public'
    #host='192.168.20.25'
    port=161
    OID_IFTABLE='1.3.6.1.2.1.2.2.1'
    indices = list(range(2, 23)) 
    temp=[]
    
    iftable=[]
    # Recuperar el numero de registrosdisponibles en la tabla
    varbinds = await slim_get(
        community, host, port,
        ObjectType(ObjectIdentity('1.3.6.1.2.1.2.1.0'))
    )
    _, num_registers = varbinds[0]
    num_registers=int(num_registers)


    # Recuperacion las propiedades de la tabla
    varBindTable = await get_bulk(
            community, host, port,
            0, num_registers,  # nonRepeaters, maxRepetitions
           *await create_object_types(OID_IFTABLE, indices)
        )
        
    for varBindRow in varBindTable:
        for varBind in varBindRow:
            oid, value = varBind
            
            temp.append(value)
            
    
    for i in range(0, len(temp), 21):
        iftable.append( {
        'ifDescr':str(temp[i]).replace('\x00', '').replace('\u0000', ''),                  
        'ifType':int(temp[i+1]),                  
        'ifMtu':int(temp[i+2]),         
        'ifSpeed':int(temp[i+3]), 
        'ifPhysAddress':'-'.join(f'{byte:02X}' for byte in temp[i+4]),
        'ifAdminStatus':int(temp[i+5]),          
        'ifOperStatus':int(temp[i+6]),         
        'ifLastChange':int(temp[i+7]),          
        'ifInOctets':int(temp[i+8]),          
        'ifInUcastPkts':int(temp[i+9]),          
        'ifInNUcastPkts':int(temp[i+10]),         
        'ifInDiscards':int(temp[i+11]),
        'ifInErrors':int(temp[i+12]),         
        'ifInUnknownProtos':int(temp[i+13]),
        'ifOutOctets':int(temp[i+14]),         
        'ifOutUcastPkts':int(temp[i+15]),        
        'ifOutNUcastPkts':int(temp[i+16]),
        'ifOutDiscards':int(temp[i+17]),         
        'ifOutErrors':int(temp[i+18]),         
        'ifOutQLen':int(temp[i+19]),  
        'ifSpecific':float(str(temp[i+20])),    
        })

    
    
    
    #with open('data.json', 'w') as file:
    #    json.dump(iftable, file, indent=4)

    return iftable
#asyncio.run(interfaceTable())