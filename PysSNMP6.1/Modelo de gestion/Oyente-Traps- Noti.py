# Listen for notifications at IPv4 & IPv6 interfaces

from pysnmp.carrier.asyncio.dispatch import AsyncioDispatcher
from pysnmp.carrier.asyncio.dgram import udp, udp6
from pyasn1.codec.ber import decoder
from pysnmp.proto import api


# noinspection PyUnusedLocal
def cbFun(transportDispatcher, transportDomain, transportAddress, wholeMsg):
    while wholeMsg:
        msgVer = int(api.decodeMessageVersion(wholeMsg))
        if msgVer in api.protoModules:
            pMod = api.protoModules[msgVer]

        else:
            print("Unsupported SNMP version %s" % msgVer)
            return

        reqMsg, wholeMsg = decoder.decode(
            wholeMsg,
            asn1Spec=pMod.Message(),
        )

        print(
            "Notification message from {}:{}: ".format(
                transportDomain, transportAddress
            )
        )

        reqPDU = pMod.apiMessage.getPDU(reqMsg)
        if reqPDU.isSameTypeWith(pMod.TrapPDU()):
            if msgVer == api.protoVersion1: 
                print(
                    "Enterprise: %s"
                    % (pMod.apiTrapPDU.getEnterprise(reqPDU).prettyPrint())
                )
                print(
                    "Agent Address: %s"
                    % (pMod.apiTrapPDU.getAgentAddr(reqPDU).prettyPrint())
                )
                print(
                    "Generic Trap: %s"
                    % (pMod.apiTrapPDU.getGenericTrap(reqPDU).prettyPrint())
                )
                print(
                    "Specific Trap: %s"
                    % (pMod.apiTrapPDU.getSpecificTrap(reqPDU).prettyPrint())
                )
                print(
                    "Uptime: %s" % (pMod.apiTrapPDU.getTimeStamp(reqPDU).prettyPrint())
                )
                varBinds = pMod.apiTrapPDU.getVarBinds(reqPDU)

            else:
                varBinds = pMod.apiPDU.getVarBinds(reqPDU)

            print("Var-binds:")

            for oid, val in varBinds:
                print(f"{oid.prettyPrint()} = {val.prettyPrint()}")

    return wholeMsg


transportDispatcher = AsyncioDispatcher()

transportDispatcher.registerRecvCbFun(cbFun)

# UDP/IPv4
transportDispatcher.registerTransport(
    udp.domainName, udp.UdpAsyncioTransport().openServerMode(("192.168.20.22", 162))
)

# UDP/IPv6
transportDispatcher.registerTransport(
    udp6.domainName, udp6.Udp6AsyncioTransport().openServerMode(("::1", 162))
)

transportDispatcher.jobStarted(1)

try:
    # Dispatcher will never finish as job#1 never reaches zero
    transportDispatcher.runDispatcher()

finally:
    transportDispatcher.closeDispatcher()