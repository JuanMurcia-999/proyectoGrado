from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
from ..slim.slim_bulk import get_bulk, slim_bulk
from ..slim.slim_get import slim_get


async def create_object_types(base_oid, indices):
    OIDs = [ObjectType(ObjectIdentity(f"{base_oid}.{i}")) for i in indices]
    return OIDs


async def interfaceTable(community, host):

    port = 161
    OID_IFTABLE = "1.3.6.1.2.1.2.2.1"
    indices = list(range(1, 23))
    temp = []

    iftable = []
    # Recuperar el numero de registrosdisponibles en la tabla
    try: 
        varbinds = await slim_get(
            community, host, port, ObjectType(ObjectIdentity("1.3.6.1.2.1.2.1.0"))
        )
        _, num_registers = varbinds[0]
        num_registers = int(num_registers)

        # Recuperacion las propiedades de la tabla
        varBindTable = await slim_bulk(
            community,
            host,
            port,
            0,
            num_registers,  # nonRepeaters, maxRepetitions
            *await create_object_types(OID_IFTABLE, indices),
        )

        for varBindRow in varBindTable:
            for varBind in varBindRow:
                oid, value = varBind

                temp.append(value)

        for i in range(0, len(temp), 22):
            iftable.append(
                {
                    "ifIndex": int(temp[i]),
                    "ifDescr": str(temp[i + 1]).replace("\x00", "").replace("\u0000", ""),
                    # "ifType": int(temp[i + 2]),
                    # "ifMtu": int(temp[i + 3]),
                    # "ifSpeed": int(temp[i + 4]),
                    "ifPhysAddress": "-".join(f"{byte:02X}" for byte in temp[i + 5]),
                    # "ifAdminStatus": int(temp[i + 6]),
                    "ifOperStatus": int(temp[i + 7]),
                    # "ifLastChange": int(temp[i + 8]),
                    "ifInOctets": int(temp[i + 9]),
                    # "ifInUcastPkts": int(temp[i + 10]),
                    "ifInNUcastPkts": int(temp[i + 11]),
                    # "ifInDiscards": int(temp[i + 12]),
                    # "ifInErrors": int(temp[i + 13]),
                    # "ifInUnknownProtos": int(temp[i + 14]),
                    "ifOutOctets": int(temp[i + 15]),   
                    # "ifOutUcastPkts": int(temp[i + 16]),
                    # "ifOutNUcastPkts": int(temp[i + 17]),
                    "ifOutDiscards": int(temp[i + 18]),
                    # "ifOutErrors": int(temp[i + 19]),
                    # "ifOutQLen": int(temp[i + 20]),
                    "ifSpecific": float(str(temp[i + 21])),
                }
            )
        return iftable
    except Exception:
        return False
