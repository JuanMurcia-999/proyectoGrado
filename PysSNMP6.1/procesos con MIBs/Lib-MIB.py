from pysnmp.smi import builder, view
from pysnmp.smi import compiler
from pysnmp.smi import rfc1902
from pysnmp import error

# Crea un constructor MIB
mibBuilder = builder.MibBuilder()

# Carga los módulos SNMPv2-MIB y SNMPv2-SMI en el constructor MIB
mibBuilder.loadModules('SNMPv2-MIB', 'SNMPv2-SMI')

# Definición de los objetos y notificaciones
snmpInPkts = builder.MibScalar((1, 3, 6, 1, 2, 1, 11, 1), rfc1902.Counter32())
snmpOutPkts = builder.MibScalar((1, 3, 6, 1, 2, 1, 11, 2), rfc1902.Counter32())
authenticationFailure = builder.NotificationType(
    (1, 3, 6, 1, 6, 3, 1, 1, 5, 5)
).setObjects(('SNMPv2-MIB', 'sysUpTime'))

# Asigna atributos adicionales
snmpInPkts.setMaxAccess("read-only").setStatus("current")
snmpOutPkts.setMaxAccess("read-only").setStatus("current")
authenticationFailure.setStatus("current").setDescription(
    "An authenticationFailure trap signifies that the SNMP entity has received a protocol message that is not properly authenticated."
)

# Exporta los símbolos
mibBuilder.exportSymbols(
    'SNMPv2-MIB',
    snmpInPkts=snmpInPkts,
    snmpOutPkts=snmpOutPkts,
    authenticationFailure=authenticationFailure
)
