from pysnmp.hlapi import *

errorIndication, errorStatus, errorIndex, varBinds = bulkWalkCmd(SnmpEngine(),
            CommunityData('public', mpModel=1),
            UdpTransportTarget(('192.168.20.22', 161)),
            ContextData(),
            0,1,
            ObjectType(ObjectIdentity('1.3.6.1.2.1'))
        
            
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
    for obj in varBinds:
        #print(varBind)
        #print(" = ".join([x.prettyPrint() for x in varBind]))
        oid = obj[0].prettyPrint()
        value = obj[1].prettyPrint()
        print(f'{oid} = {value}')





  