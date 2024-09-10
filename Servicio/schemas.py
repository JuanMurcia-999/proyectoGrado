from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime, date, time



# esquema de datos para los elementos de la tabla Agents


class TypeBase(BaseModel):
    id_type: int
    type_name: str

    class Config:
        from_attributes = True


# Escritura
class CreateAgent(BaseModel):
    ag_name: str | None
    ip_address: str | None
    ag_type: int | None


# Lectura
class Agent(CreateAgent):
    id_agent: int | None

    class Config:
        from_attributes = True


# lectura de angesntes con Types
class AgentWithType(Agent):
    type: TypeBase  # Incluye la información del tipo

    class Config:
        from_attributes = True


# features


class new_features(BaseModel):
    id_adminis: int | None
    id_sensor: int | None
    ag_name: str
    id_agent: int
    oid: str
    adminis_name: str
    timer: int


class features(BaseModel):
    id_agent: int
    oid: str
    adminis_name: str
    timer: int

    class config:
        from_attributes = True


class Features(features):
    id_adminis: int | None
    id_sensor: int | None

    class config:
        from_attributes = True


# lectura de features con agentes
class FeatureswithAgent(Features):
    agent: Agent

    class Config:
        from_attributes = True


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


# crear sensor
class SensorCreate(BaseModel):
    ID: str
    Ip: str
    oid: str
    description: str
    interval: str


class addHistory(BaseModel):
    id_agent: int
    id_adminis: int
    value: Any


class readHistory(addHistory):
    id_register: int
    date: date
    time: time

    class config:
        from_attributes = True


class historywithfeature(readHistory):
    feature: Features

    class config:
        from_attributes = True


class getHistory(BaseModel):
    id_agent: int
    id_sensor: int | None
    id_adminis: int


class statistics(BaseModel):
    min: float | int
    max: float | int
    avg: float | int


class DataModel(BaseModel):
    datagrafic: list[Any]


class MainModel(BaseModel):
    data: DataModel


class filterHistory(BaseModel):
    id_agent: int | Any
    id_adminis: int | Any
    id_sensor: int | Any
    datebase: str | Any
    timebase: str | Any
    daterange: str | Any
    timerange: str | Any
    limit: int | Any
    offset: int | Any


# /////////////Modelos de los gestionables establecidos//////////////


class stoptask(BaseModel):
    name: str
    nametask: str
    id_agent: int
    id_feature: int


class Manageable(stoptask):
    params: Dict[str, Any]


class addDefaultFeature(BaseModel):
    id_feature: int
    fe_name: str
    id_type: int

    class config:
        from_attributes = True


class Addactivedefault(BaseModel):
    id_feature: int
    id_agent: int

    class config:
        from_attributes = True


class ReadAddactivedefault(Addactivedefault):
    id_active: int

    class config:
        from_attributes = True


class ActiveWithFeature(ReadAddactivedefault):
    features: addDefaultFeature

    class Config:
        from_attributes = True


# -----------------------------------------------------------------------------------ALARMAS


class newAlarm(BaseModel):

    id_agent: int
    id_adminis: int
    id_sensor: int | None
    operation: str
    value: float
    counter: int | None


class readAlarm(newAlarm):
    id_alarm: int


# -------------------------------------------- taskoid


class elements(BaseModel):
    ID: int
    IP: str
    TIMES: list[int]
    OIDS: list[list[str]]
    IDF: list[list[int]]


class taskoid(BaseModel):
    TIME: int
    OIDS: list[Any]
    ID: int
    IDF: list[int]
    IP: str


# ---------------------------------------------------Manageable


# ---------------------------------------------------Gestionables


class ConfigAnchoBanda(BaseModel):
    ip: str
    Num_Interface: str
    intervalo: int | None
    id_adminis: int
    id: int

    class Config:
        arbitrary_types_allowed = True


class ConfigProcesses(BaseModel):
    ip: str
    timer: int | None
    id_adminis: int
    id: int

    class Config:
        arbitrary_types_allowed = True


# --------------------------- pruebas


class ReadDefaultFeature(BaseModel):
    id_feature: int
    fe_name: str
