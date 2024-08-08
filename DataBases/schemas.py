from pydantic import BaseModel
from datetime import datetime

#esquema de datos para los elementos de la tabla Agents


#Escritura
class CreateAgent(BaseModel):
    Hostname:str
    IP_address:str
    ag_type:str

#Lectura
class Agent(CreateAgent):
    ID_agent:int


# Lectura de features
class new_features(BaseModel):
    id_agent :int
    ip_agent:str
    oid: str
    description:str
    timer : int

class Features(new_features):
    id_feature:int



class iftable(BaseModel):
        ifDescr:str    
        ifType:int           
        ifMtu:int    
        ifSpeed:int
        ifPhysAddress:str
        ifAdminStatus:int     
        ifOperStatus:int       
        ifLastChange:int        
        ifInOctets:int       
        ifInDiscards:int
        ifInErrors:int     
        ifInUnknownProtos:int
        ifOutOctets:int       
        ifOutUcastPkts:int     
        ifOutNUcastPkts:int
        ifOutDiscards:int 
        ifOutErrors:int       
        ifOutQLen:int
        ifSpecific:float

# crear sensor
class SensorCreate(BaseModel):
    ID:str
    Ip:str
    oid:str
    description:str
    interval: str

class SensorRead():
    pass


class addHistory(BaseModel):
    ip_agent:str
    oid:str
    value:str

class readHistory(addHistory):
    id_his_feature:int
    created_at:datetime


class getHistory(BaseModel):
    ip_agent:str
    oid:str

class responseHistory(BaseModel):
    value:list[str]
    created_at:list[str]


#/////////////Modelos de los gestionables establecidos//////////////

class addDefaultFeature(BaseModel):
    fe_name:str
    ag_type: str

class stoptask(BaseModel):
    name:str
    nametask:str

    
class Manageable(stoptask):
    ip:str
  

