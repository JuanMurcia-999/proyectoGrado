import sys
import os
import asyncio

# Añade el directorio raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))# Listen for notifications at IPv4 & IPv6 interfaces
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../Servicio")))#
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Utilizables")))
from pysnmp.carrier.asyncio.dispatch import AsyncioDispatcher
from pysnmp.carrier.asyncio.dgram import udp, udp6
from pyasn1.codec.ber import decoder
from pysnmp.proto import api
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Servicio import models
from Servicio.Utilizables.BotTelegram import sendmessage

DATABASE_URL = "sqlite:///C:/Users/Juan Murcia/Desktop/Proyecto de grado/Desarrollo/Recolector/Servicio/GestorDB.sqlite"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()



# noinspection PyUnusedLocal
def cbFun(transportDispatcher, transportDomain, transportAddress, wholeMsg):
    while wholeMsg:
        msgVer = int(api.decodeMessageVersion(wholeMsg))
        if msgVer in api.protoModules:
            pMod = api.protoModules[msgVer]

        else:
            # print("Unsupported SNMP version %s" % msgVer)
            return

        reqMsg, wholeMsg = decoder.decode(
            wholeMsg,
            asn1Spec=pMod.Message(),
        )

        # print(
        #     "Notification message from {}:{}: ".format(
        #         transportDomain, transportAddress
        #     )
        # )
        log_message = ""

        reqPDU = pMod.apiMessage.getPDU(reqMsg)
        if reqPDU.isSameTypeWith(pMod.TrapPDU()):
            if msgVer == api.protoVersion1: 
                enterprise = pMod.apiTrapPDU.getEnterprise(reqPDU).prettyPrint()
                agent_address = pMod.apiTrapPDU.getAgentAddr(reqPDU).prettyPrint()
                generic_trap = pMod.apiTrapPDU.getGenericTrap(reqPDU).prettyPrint()
                specific_trap = pMod.apiTrapPDU.getSpecificTrap(reqPDU).prettyPrint()
                uptime = pMod.apiTrapPDU.getTimeStamp(reqPDU).prettyPrint()
                
                # Guardar la IP en una segunda variable
                ip_address = agent_address

                log_message += f"Enterprise: {enterprise}\n"
                log_message += f"Agent Address: {agent_address}\n"
                log_message += f"Generic Trap: {generic_trap}\n"
                log_message += f"Specific Trap: {specific_trap}\n"
                log_message += f"Uptime: {uptime}\n"
                
                varBinds = pMod.apiTrapPDU.getVarBinds(reqPDU)
            else:
                varBinds = pMod.apiPDU.getVarBinds(reqPDU)

            log_message += "Var-binds:\n"
            
            for oid, val in varBinds:
                log_message += f"{oid.prettyPrint()} = {val.prettyPrint()}\n"
            
            # Imprimir el mensaje de log
            print(log_message)

            # Opcional: Imprimir la IP almacenada en la variable ip_address
            print(f"IP Address: {ip_address}")
            try:
                trap = models.Traps(
                    ip= ip_address,
                    message = log_message
                )
                db.add(trap)
                db.commit()
                db.refresh(trap)
                db.close
                sendmessage(log_message)
            except Exception as e:
                print(e)
                

    return wholeMsg


transportDispatcher = AsyncioDispatcher()

transportDispatcher.registerRecvCbFun(cbFun)

# UDP/IPv4
transportDispatcher.registerTransport(
    udp.domainName, udp.UdpAsyncioTransport().openServerMode(("192.168.20.9", 162))
)

transportDispatcher.jobStarted(1)

try:
    # Dispatcher will never finish as job#1 never reaches zero
    transportDispatcher.runDispatcher()

finally:
    transportDispatcher.closeDispatcher()

