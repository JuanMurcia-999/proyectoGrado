from sqlalchemy.orm import Session
import models,schemas

# Peticion que retorna todos los agentes en la base de datos
def get_all_agent(db:Session):
    return db.query(models.Agents).all()

#Query para creacion de Agents
def create_agent(db:Session, agent: schemas.CreateAgent):

    db_agent= models.Agents(Hostname= agent.Hostname,
                            IP_address =agent.IP_address)
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

