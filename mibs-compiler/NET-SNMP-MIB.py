# SNMP MIB module (NET-SNMP-MIB) expressed in pysnmp data model.
#
# This Python module is designed to be imported and executed by the
# pysnmp library.
#
# See https://www.pysnmp.com/pysnmp for further information.
#
# Notes
# -----
# ASN.1 source file://C:\Users\Juan Murcia\Desktop\Proyecto de grado\mibs\NET-SNMP-MIB.txt
# Produced by pysmi-1.4.3 at Thu Aug  8 03:47:19 2024
# On host ? platform ? version ? by user ?
# Using Python version 3.12.4 (tags/v3.12.4:8e8a4ba, Jun  6 2024, 19:30:16) [MSC v.1940 64 bit (AMD64)]

if 'mibBuilder' not in globals():
    import sys

    sys.stderr.write(__doc__)
    sys.exit(1)

# Import base ASN.1 objects even if this MIB does not use it

(Integer,
 OctetString,
 ObjectIdentifier) = mibBuilder.importSymbols(
    "ASN1",
    "Integer",
    "OctetString",
    "ObjectIdentifier")

(NamedValues,) = mibBuilder.importSymbols(
    "ASN1-ENUMERATION",
    "NamedValues")
(ConstraintsIntersection,
 SingleValueConstraint,
 ValueRangeConstraint,
 ValueSizeConstraint,
 ConstraintsUnion) = mibBuilder.importSymbols(
    "ASN1-REFINEMENT",
    "ConstraintsIntersection",
    "SingleValueConstraint",
    "ValueRangeConstraint",
    "ValueSizeConstraint",
    "ConstraintsUnion")

# Import SMI symbols from the MIBs this MIB depends on

(ModuleCompliance,
 NotificationGroup) = mibBuilder.importSymbols(
    "SNMPv2-CONF",
    "ModuleCompliance",
    "NotificationGroup")

(TimeTicks,
 MibScalar,
 MibTable,
 MibTableRow,
 MibTableColumn,
 Gauge32,
 Counter32,
 iso,
 ObjectIdentity,
 IpAddress,
 NotificationType,
 enterprises,
 Counter64,
 MibIdentifier,
 Unsigned32,
 Integer32,
 ModuleIdentity,
 Bits) = mibBuilder.importSymbols(
    "SNMPv2-SMI",
    "TimeTicks",
    "MibScalar",
    "MibTable",
    "MibTableRow",
    "MibTableColumn",
    "Gauge32",
    "Counter32",
    "iso",
    "ObjectIdentity",
    "IpAddress",
    "NotificationType",
    "enterprises",
    "Counter64",
    "MibIdentifier",
    "Unsigned32",
    "Integer32",
    "ModuleIdentity",
    "Bits")

(DisplayString,
 TextualConvention) = mibBuilder.importSymbols(
    "SNMPv2-TC",
    "DisplayString",
    "TextualConvention")


# MODULE-IDENTITY

netSnmp = ModuleIdentity(
    (1, 3, 6, 1, 4, 1, 8072)
)
netSnmp.setRevisions(
        ("2002-01-30 00:00",)
)


# Types definitions


# TEXTUAL-CONVENTIONS



# MIB Managed Objects in the order of their OIDs

_NetSnmpObjects_ObjectIdentity = ObjectIdentity
netSnmpObjects = _NetSnmpObjects_ObjectIdentity(
    (1, 3, 6, 1, 4, 1, 8072, 1)
)
_NetSnmpEnumerations_ObjectIdentity = ObjectIdentity
netSnmpEnumerations = _NetSnmpEnumerations_ObjectIdentity(
    (1, 3, 6, 1, 4, 1, 8072, 3)
)
_NetSnmpModuleIDs_ObjectIdentity = ObjectIdentity
netSnmpModuleIDs = _NetSnmpModuleIDs_ObjectIdentity(
    (1, 3, 6, 1, 4, 1, 8072, 3, 1)
)
_NetSnmpAgentOIDs_ObjectIdentity = ObjectIdentity
netSnmpAgentOIDs = _NetSnmpAgentOIDs_ObjectIdentity(
    (1, 3, 6, 1, 4, 1, 8072, 3, 2)
)
_NetSnmpDomains_ObjectIdentity = ObjectIdentity
netSnmpDomains = _NetSnmpDomains_ObjectIdentity(
    (1, 3, 6, 1, 4, 1, 8072, 3, 3)
)
_NetSnmpNotificationPrefix_ObjectIdentity = ObjectIdentity
netSnmpNotificationPrefix = _NetSnmpNotificationPrefix_ObjectIdentity(
    (1, 3, 6, 1, 4, 1, 8072, 4)
)
_NetSnmpNotifications_ObjectIdentity = ObjectIdentity
netSnmpNotifications = _NetSnmpNotifications_ObjectIdentity(
    (1, 3, 6, 1, 4, 1, 8072, 4, 0)
)
_NetSnmpNotificationObjects_ObjectIdentity = ObjectIdentity
netSnmpNotificationObjects = _NetSnmpNotificationObjects_ObjectIdentity(
    (1, 3, 6, 1, 4, 1, 8072, 4, 1)
)
_NetSnmpConformance_ObjectIdentity = ObjectIdentity
netSnmpConformance = _NetSnmpConformance_ObjectIdentity(
    (1, 3, 6, 1, 4, 1, 8072, 5)
)
_NetSnmpCompliances_ObjectIdentity = ObjectIdentity
netSnmpCompliances = _NetSnmpCompliances_ObjectIdentity(
    (1, 3, 6, 1, 4, 1, 8072, 5, 1)
)
_NetSnmpGroups_ObjectIdentity = ObjectIdentity
netSnmpGroups = _NetSnmpGroups_ObjectIdentity(
    (1, 3, 6, 1, 4, 1, 8072, 5, 2)
)
_NetSnmpExperimental_ObjectIdentity = ObjectIdentity
netSnmpExperimental = _NetSnmpExperimental_ObjectIdentity(
    (1, 3, 6, 1, 4, 1, 8072, 9999)
)
_NetSnmpPlaypen_ObjectIdentity = ObjectIdentity
netSnmpPlaypen = _NetSnmpPlaypen_ObjectIdentity(
    (1, 3, 6, 1, 4, 1, 8072, 9999, 9999)
)

# Managed Objects groups


# Notification objects


# Notifications groups


# Agent capabilities


# Module compliance


# Export all MIB objects to the MIB builder

mibBuilder.exportSymbols(
    "NET-SNMP-MIB",
    **{"netSnmp": netSnmp,
       "netSnmpObjects": netSnmpObjects,
       "netSnmpEnumerations": netSnmpEnumerations,
       "netSnmpModuleIDs": netSnmpModuleIDs,
       "netSnmpAgentOIDs": netSnmpAgentOIDs,
       "netSnmpDomains": netSnmpDomains,
       "netSnmpNotificationPrefix": netSnmpNotificationPrefix,
       "netSnmpNotifications": netSnmpNotifications,
       "netSnmpNotificationObjects": netSnmpNotificationObjects,
       "netSnmpConformance": netSnmpConformance,
       "netSnmpCompliances": netSnmpCompliances,
       "netSnmpGroups": netSnmpGroups,
       "netSnmpExperimental": netSnmpExperimental,
       "netSnmpPlaypen": netSnmpPlaypen}
)
