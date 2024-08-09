from pydantic import BaseModel
from datetime import datetime, date, time

#esquema de datos para los elementos de la tabla Agents


class TypeBase(BaseModel):
    id_type: int
    type_name: str

    class Config:
        orm_mode = True


#Escritura
class CreateAgent(BaseModel):
    ag_name:str
    ip_address:str
    ag_type:int

#Lectura
class Agent(CreateAgent):
    id_agent:int
    
    class Config:
        orm_mode = True



class AgentWithType(Agent):
    type: TypeBase  # Incluye la información del tipo

    class Config:
        orm_mode = True









# Lectura de features
class new_features(BaseModel):
    id_agent :int
    oid: str
    adminis_name:str
    timer : int

    class config:
        orm_mode=True 


class Features(new_features):
    id_adminis:int

    class config:
        orm_mode=True 

class FeatureswithAgent(Features):
    agent: Agent

    class Config:
        orm_mode = True






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


class addHistory(BaseModel):
    id_agent:int
    id_adminis:int
    value:str

class readHistory(addHistory):
    id_register:int
    date:date
    time:time


class getHistory(BaseModel):
    id_agent:int
    id_adminis:int


class responseHistory(BaseModel):
    value:list[str]
    created_at:list[str]


#/////////////Modelos de los gestionables establecidos//////////////

class addDefaultFeature(BaseModel):
    fe_name:str
    id_type:int



class stoptask(BaseModel):
    name:str
    nametask:str

    
class Manageable(stoptask):
    ip:str
  

