from pydantic import BaseModel
from typing import Dict, Any
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


# lectura de angesntes con Types
class AgentWithType(Agent):
    type: TypeBase  # Incluye la información del tipo

    class Config:
        orm_mode = True






#features
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

#lectura de features con agentes
class FeatureswithAgent(Features):
    agent: Agent

    class Config:
        orm_mode = True





class iftable(BaseModel):
        ifIndex:int
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


class HistoryWithFeature():
    pass








class getHistory(BaseModel):
    id_agent:int
    id_adminis:int


class responseHistory(BaseModel):
    value:list[str]
    created_at:list[str]


#/////////////Modelos de los gestionables establecidos//////////////


    
class stoptask(BaseModel):
    name:str
    nametask:str
    id_agent:int
    id_feature:int

    
class Manageable(stoptask):
    params: Dict[str, Any]


class addDefaultFeature(BaseModel):
    id_feature:int
    fe_name:str
    id_type:int
    class config:
        orm_mode = True



class Addactivedefault(BaseModel):
    id_feature:int
    id_agent:int

    class config:
        orm_mode = True    


class ReadAddactivedefault(Addactivedefault):
    id_active:int

    class config:
        orm_mode = True

class ActiveWithFeature(ReadAddactivedefault):
    features: addDefaultFeature

    class Config:
        orm_mode=True


#--------------------------- pruebas

class ReadDefaultFeature(BaseModel):
    id_feature:int
    fe_name:str