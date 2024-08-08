from sqlalchemy.orm import Session
from sqlalchemy import or_
import models,schemas


# Peticion que retorna todos los agentes en la base de datos
def get_all_agent(db:Session):
    return db.query(models.Agents).all()

#Query para creacion de Agents
def create_agent(db:Session, agent: schemas.CreateAgent):
    db_agent= models.Agents(
        Hostname= agent.Hostname,
        IP_address =agent.IP_address,
        ag_type=agent.ag_type )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

#Query para eleiminacion de agentes
def delete_agent(db: Session, field,value):
    db_agent = db.query(models.Agents).filter( getattr(models.Agents,field) == value).first()
    if db_agent:
        db.delete(db_agent)
        db.commit()
        return "agente eliminado"
    return "Este agente ya fue eliminado o no existe"

# Query para obtener todas las caracteristicas que son monitoreadas
def get_all_features(db: Session):
    return db.query(models.Managed_features).all()

# Query para obtener todas las caracteristicas segun agente
def get_all_features_agent(db: Session,value):
    return db.query(models.Managed_features).filter( models.Managed_features.ip_agent == value)

# Agregar una nueva feature a monitorizar
def new_feature(db:Session, feature: schemas.new_features):

    db_agent= models.Managed_features(
    id_agent=feature.id_agent, 
    ip_agent = feature.ip_agent,
    description = feature.description,
    oid= feature.oid, 
    timer=feature.timer)

    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

#Query para eleiminacion de features
def delete_feature(db: Session,field,value):
    db_agent = db.query(models.Managed_features).filter( getattr(models.Managed_features,field) == value).first()
    if db_agent:
        db.delete(db_agent)
        db.commit()
        return "feature eliminada"
    return "Esta feature ya fue eliminado o no existe"

# Agregar un nuevo registro al historial
def add_history(db:Session, record: schemas.addHistory):

    db_history= models.History_features  (
        #id_his_feature=record.id_his_feature,
        ip_agent=record.ip_agent,
        oid=record.oid,
        value=record.value
        )

    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def get_all_history(db:Session):
    return db.query(models.History_features).all()

def get_history_sensor(db:Session,filter:schemas.getHistory):
    response = db.query(models.History_features.value,models.History_features.created_at).filter(models.History_features.oid == filter.oid  ,models.History_features.ip_agent == filter.ip_agent)
    values = [item[0] for item in response]
    date =  [item[1].strftime('%Y-%m-%d %H:%M:%S')    for item in response]
    return {
        'value': values,
        'created_at': date
    }


# Lista de features preestablecidas segun el tipo

def add_default_feature(db:Session, feature: schemas.addDefaultFeature):

    db_defFeatures= models.Default_features  (
        fe_name= feature.fe_name,
        ag_type = feature.ag_type
            )

    db.add(db_defFeatures)
    db.commit()
    db.refresh(db_defFeatures)
    return db_defFeatures

def get_all_default_features(db: Session,value):
    return db.query(models.Default_features).filter( or_( models.Default_features.ag_type == value ,
                                                          models.Default_features.ag_type == 'all')).all()
