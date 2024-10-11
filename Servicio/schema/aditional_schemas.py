from pydantic import BaseModel

class operation(BaseModel):
    ip:str
    oid:str
    value: str|int|None


class iftable(BaseModel):
    ifIndex: int
    ifDescr: str
    # ifType: int
    # ifMtu: int
    # ifSpeed: int
    ifPhysAddress: str
    # ifAdminStatus: int
    ifOperStatus: int
    # ifLastChange: int
    ifInOctets: int
    # ifInDiscards: int
    # ifInErrors: int
    # ifInUnknownProtos: int
    ifOutOctets: int
    # ifOutUcastPkts: int
    # ifOutNUcastPkts: int
    ifOutDiscards: int
    # ifOutErrors: int
    # ifOutQLen: int
    ifSpecific: float
