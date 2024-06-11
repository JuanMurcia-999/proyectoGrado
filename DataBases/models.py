from sqlalchemy import Column,ForeignKey, Integer,String
from sqlalchemy.orm import relationship

from database import Base

from enum import Enum

#Definicion de los modelos de datos extras


#Eliminacion de agente segun columna

class ModelField(str, Enum):
    ID_agent = "ID agent"
    Hostname = "Host name"
    IP_address = "IP"



# Definicion de la TABLA Agentes(Agents)

class Agents(Base):
    __tablename__ ="Agents"

    ID_agent = Column(Integer, autoincrement=True,primary_key=True)
    Hostname = Column(String, nullable=False,unique=True)
    IP_address=Column(String,nullable=False,unique=True)



    
