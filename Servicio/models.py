from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Date,
    Time,
    Text,
    Numeric,
    Float,
)
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.sql import func  # Se mantiene la importación de func
from enum import Enum

# Definición de los modelos de datos extras


# Eliminación de agente según columna
class ModelField(str, Enum):
    id_agent = "ID"
    ag_name = "name"
    ip_address = "IP"


class ModelFieldSensor(str, Enum):
    id_agent = "id_agente"
    oid = "oid"
    id_adminis = "id_adminis"


# Definición de la TABLA Agentes (Agents)
class Types(Base):
    __tablename__ = "types"

    id_type = Column(Integer, autoincrement=True, primary_key=True)
    type_name = Column(String, nullable=False, unique=True)

    agents = relationship("Agents", back_populates="type")
    defaultfeatures = relationship("Default_features", back_populates="type")


class Agents(Base):
    __tablename__ = "agents"

    id_agent = Column(Integer, autoincrement=True, primary_key=True)
    ag_name = Column(String, nullable=False, unique=True)
    ip_address = Column(String, nullable=False, unique=True)
    ag_type = Column(Integer, ForeignKey("types.id_type"), nullable=False)

    type = relationship("Types", back_populates="agents")
    features = relationship(
        "Administered_features", cascade="all, delete", back_populates="agent"
    )
    history = relationship("History_features", cascade="all, delete", back_populates="agent")
    Alarms = relationship("Alarms", cascade="all, delete")
    Actives = relationship("Active_default", cascade="all,delete",back_populates="agents")


class Administered_features(Base):
    __tablename__ = "administered_features"

    id_adminis = Column(Integer, autoincrement=True, primary_key=True)
    id_sensor = Column(Integer, nullable=True)
    id_agent = Column(Integer, ForeignKey("agents.id_agent"), nullable=False)
    oid = Column(String, nullable=False)
    adminis_name = Column(String, nullable=False)
    timer = Column(Integer, nullable=False)

    agent = relationship("Agents", back_populates="features")
    alarms = relationship(
        "Alarms",
        back_populates="administered_feature",
        cascade="all, delete, delete-orphan",
    )


class Default_features(Base):
    __tablename__ = "default_features"

    id_feature = Column(Integer, autoincrement=True, primary_key=True)
    fe_name = Column(String, nullable=False)
    id_type = Column(Integer, ForeignKey("types.id_type"), nullable=False)

    type = relationship("Types", back_populates="defaultfeatures")


class Active_default(Base):
    __tablename__ = "active_default"

    id_active = Column(Integer, autoincrement=True)
    id_feature = Column(
        Integer, ForeignKey("default_features.id_feature"), nullable=False, primary_key=True
    )
    id_agent = Column(Integer, ForeignKey("agents.id_agent"), nullable=False, primary_key=True)
    params = Column(Text, nullable=True)

    features = relationship("Default_features")
    agents = relationship("Agents" , back_populates="Actives")


class History_features(Base):
    __tablename__ = "history_features"

    id_register = Column(Integer, autoincrement=True, primary_key=True)
    id_agent = Column(Integer, ForeignKey("agents.id_agent"), nullable=False)
    id_adminis = Column(
        Integer, ForeignKey("administered_features.id_adminis"), nullable=False
    )
    value = Column(Float, nullable=False)

    date = Column(String)
    time = Column(String)

    agent = relationship("Agents", back_populates="history")
    feature = relationship("Administered_features")


class Alarms(Base):
    __tablename__ = "alarms"

    id_alarm = Column(Integer, autoincrement=True, primary_key=True)
    id_agent = Column(Integer, ForeignKey("agents.id_agent"), nullable=False)
    id_adminis = Column(
        Integer, ForeignKey("administered_features.id_adminis"), nullable=True
    )
    id_sensor = Column(Integer, nullable=True)
    operation = Column(String, nullable=False)
    value = Column(Integer, nullable=False)
    counter = Column(Integer, nullable=True)

    administered_feature = relationship(
        "Administered_features", back_populates="alarms"
    )

class Traps(Base):
    __tablename__ = "traps"

    id_alarm = Column(Integer, autoincrement=True, primary_key=True)
    ip = Column(String, nullable=False)
    message = Column(Text, nullable=True)
    date = Column(Date, server_default=func.current_date())
    time = Column(Time, server_default=func.current_time())
