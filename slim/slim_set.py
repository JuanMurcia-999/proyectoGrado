import asyncio
from pysnmp.hlapi.asyncio import setCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity
from pysnmp.smi.error import SmiError

async def Set(community, host, port,oid,value):
    try:
        # Supongamos que estos valores son los que estás utilizando en la llamada a setCmd
        errorIndication, errorStatus, errorIndex, varBinds = await setCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((host, port)),
            ContextData(),
            ObjectType(ObjectIdentity(oid), value)  # Valor problemático
        )

        # Aquí procesas los resultados si no ocurre un error
        if errorIndication:
            print(f"Error de SNMP: {errorIndication}")
        elif errorStatus:
            print(f"Error en el estado SNMP: {errorStatus.prettyPrint()}")
        else:
            for varBind in varBinds:
                print(f'{varBind[0]} = {varBind[1]}')
            return True

    except SmiError as e:
        print(f"Error al intentar realizar el setCmd: {e}")
        return False
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        return False

# Ejecutar la función asincrónica
# asyncio.run(Set())