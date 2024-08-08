from sqlalchemy import Column,ForeignKey, Integer,String,DateTime
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.sql import func
from enum import Enum

#Definicion de los modelos de datos extras


#Eliminacion de agente segun columna

class ModelField(str, Enum):
    ID_agent = "ID agent"
    Hostname = "Host name"
    IP_address = "IP"

class ModelFieldSensor(str, Enum):
    #id_agent ="id_agent"
    ip_agent="ip_agent"
    oid ="oid"
    #description="description"
    #timer ="timer"
    id_feature="id_feature"


# Definicion de la TABLA Agentes(Agents)

class Agents(Base):
    __tablename__ ="agents"

    ID_agent = Column(Integer, autoincrement=True,primary_key=True)
    Hostname = Column(String, nullable=False,unique=True)
    IP_address=Column(String,nullable=False,unique=True)
    ag_type= Column(String, nullable=False)

    feature=relationship("Managed_features",cascade='all,delete')

class Managed_features(Base):
    __tablename__ = "managed_features"

    id_feature = Column(Integer, autoincrement=True,primary_key=True)
    id_agent = Column(Integer,ForeignKey("agents.ID_agent"),nullable=False)
    oid= Column(String, nullable=True, default='N/A')
    description= Column(String, nullable=False)
    ip_agent= Column(String, nullable=False)
    timer = Column(Integer, nullable=False)
    
 
class Default_features(Base):
    __tablename__ ='default_features'

    id_feature = Column(Integer, autoincrement=True,primary_key=True)
    fe_name = Column(String, nullable=False)
    ag_type =Column(String, nullable=False)



class History_features(Base):
    __tablename__ ="history_features"

    id_his_feature = Column(Integer, autoincrement=True,primary_key=True)
    ip_agent= Column(String, nullable=False)
    oid= Column(String, nullable=False)
    value =Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
