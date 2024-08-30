from pysnmp.carrier.asyncio.dispatch import AsyncioDispatcher
from pysnmp.carrier.asyncio.dgram import udp, udp6
from pyasn1.codec.ber import encoder, decoder
from pysnmp.proto import api
import time, bisect
from gestionables import *


# Index for fast lookup of OIDs
mibInstrIdx = {}
for mibVar in mibInstr:
    if isinstance(mibVar, SysEntryIndex) or isinstance(mibVar, SysEntryValue) or isinstance(mibVar, DiskEntryValue):
        mibInstrIdx[mibVar.name + (mibVar.index,)] = mibVar
    else:
        mibInstrIdx[mibVar.name] = mibVar


def cbFun(transportDispatcher, transportDomain, transportAddress, wholeMsg):
    while wholeMsg:
        msgVer = api.decodeMessageVersion(wholeMsg)
        if msgVer in PROTOCOL_MODULES:
            pMod = PROTOCOL_MODULES[msgVer]
        else:
            print("Unsupported SNMP version %s" % msgVer)
            return
        reqMsg, wholeMsg = decoder.decode(
            wholeMsg,
            asn1Spec=pMod.Message(),
        )
        rspMsg = pMod.apiMessage.getResponse(reqMsg)
        rspPDU = pMod.apiMessage.getPDU(rspMsg)
        reqPDU = pMod.apiMessage.getPDU(reqMsg)
        varBinds = []
        pendingErrors = []
        errorIndex = 0

        # Handle GETNEXT PDU
        if reqPDU.isSameTypeWith(pMod.GetNextRequestPDU()):
            for oid, val in pMod.apiPDU.getVarBinds(reqPDU):
                errorIndex += 1
                nextIdx = bisect.bisect(
                    mibInstr,
                    oid,
                    key=lambda x: (
                        x.name + (x.index,)
                        if isinstance(x, (SysEntryIndex, SysEntryValue))
                        else x.name
                    ),
                )
                if nextIdx == len(mibInstr):
                    varBinds.append((oid, val))
                    pendingErrors.append((pMod.apiPDU.setEndOfMibError, errorIndex))
                else:
                    nextVar = mibInstr[nextIdx]
                    varBinds.append(
                        (
                            (
                                nextVar.name + (nextVar.index,)
                                if isinstance(nextVar, (SysEntryIndex, SysEntryValue))
                                else nextVar.name
                            ),
                            nextVar(msgVer),
                        )
                    )

        # Handle GET PDU
        elif reqPDU.isSameTypeWith(pMod.GetRequestPDU()):
            for oid, val in pMod.apiPDU.getVarBinds(reqPDU):
                if oid in mibInstrIdx:
                    varBinds.append((oid, mibInstrIdx[oid](msgVer)))
                else:
                    varBinds.append((oid, val))
                    pendingErrors.append(
                        (pMod.apiPDU.setNoSuchInstanceError, errorIndex)
                    )
                    break
        else:
            pMod.apiPDU.setErrorStatus(rspPDU, "genErr")

        pMod.apiPDU.setVarBinds(rspPDU, varBinds)
        for f, i in pendingErrors:
            f(rspPDU, i)
        transportDispatcher.sendMessage(
            encoder.encode(rspMsg), transportDomain, transportAddress
        )
    return wholeMsg


def get_external_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No es necesario que el servidor real exista o responda
        s.connect(("8.8.8.8", 80))
        external_ip = s.getsockname()[0]
    finally:
        s.close()
    return external_ip


# Obtener y mostrar la IP de la interfaz principal conectada a internet
while True:

    # Setting up the SNMP agent
    transportDispatcher = AsyncioDispatcher()
    transportDispatcher.registerRecvCbFun(cbFun)

    # Register UDP/IPv4 transport
    transportDispatcher.registerTransport(
        "udpDomain", udp.UdpAsyncioTransport().openServerMode((get_external_ip(), 165))
    )

    # Register UDP/IPv6 transport
    transportDispatcher.registerTransport(
        "udp6Domain", udp6.Udp6AsyncioTransport().openServerMode(("::1", 165))
    )

    transportDispatcher.jobStarted(1)

    try:
        # Dispatcher will never finish as job#1 never reaches zero
        transportDispatcher.runDispatcher()
    except:
        transportDispatcher.closeDispatcher()
        raise
