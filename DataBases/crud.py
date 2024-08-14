from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_,and_
import models,schemas
import json

# Peticion que retorna todos los agentes en la base de datos
def get_all_agent(db:Session):
    return db.query(models.Agents).options(joinedload(models.Agents.type)).all()


#Query para creacion de Agents
def create_agent(db:Session, agent: schemas.CreateAgent):
    db_agent= models.Agents(
        ag_name= agent.ag_name,
        ip_address =agent.ip_address,
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
    return db.query(models.Administered_features).options(joinedload(models.Administered_features.agent)).all()

# Query para obtener todas las caracteristicas segun agente
def get_all_features_agent(db: Session,value):
    return db.query(models.Administered_features).filter( 
        models.Administered_features.id_agent ==value).options(
            joinedload(models.Administered_features.agent)
        )

# Agregar una nueva feature a monitorizar
def new_feature(db:Session, feature: schemas.new_features):

    db_agent= models.Administered_features(
    id_agent=feature.id_agent, 
    oid= feature.oid, 
    adminis_name = feature.adminis_name,
    timer=feature.timer)

    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

#Query para eleiminacion de features
def delete_feature(db: Session,field,value):
    db_agent = db.query(models.Administered_features).filter( getattr(models.Administered_features,field) == value).first()
    if db_agent:
        db.delete(db_agent)
        db.commit()
        return "feature eliminada"
    return "Esta feature ya fue eliminado o no existe"

# Agregar un nuevo registro al historial
def add_history(db:Session, record: schemas.addHistory):

    db_history= models.History_features  (
        #id_his_feature=record.id_his_feature,
        id_agent=record.id_agent,
        id_adminis=record.id_adminis,
        value=record.value
        )

    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def get_all_history(db:Session):
    return db.query(models.History_features).all()

def get_history_sensor(db:Session,filter:schemas.getHistory):
    response = db.query(models.History_features.value,models.History_features.date).filter(
        models.History_features.id_adminis == filter.id_adminis  ,models.History_features.id_agent == filter.id_agent).order_by(
            models.History_features.id_register.desc()
        )
    values = [item[0] for item in response]
    date =  [item[1].strftime('%Y-%m-%d')    for item in response]
    return {
        'value': values,
        'created_at': date
    }


# Lista de features preestablecidas segun el tipo

def add_default_feature(db:Session, feature: schemas.addDefaultFeature):

    db_defFeatures= models.Default_features(
        fe_name= feature.fe_name,
        id_type = feature.id_type
            )

    db.add(db_defFeatures)
    db.commit()
    db.refresh(db_defFeatures)
    return db_defFeatures


def get_all_default_features(db: Session,value):
    return db.query(models.Default_features).filter( or_( models.Default_features.id_type == value ,
                                                          models.Default_features.id_type == 1)).all()


def get_active_default(db:Session,value):
    return db.query(models.Active_default).all()

def get_active_default_prueba(db:Session):
    return db.query(models.Active_default).options(joinedload(models.Active_default.features)).all()



def add_active_default(db:Session, dates: schemas.Manageable):
    params_json =json.dumps(dates.params)
    addactive = models.Active_default(
        id_feature = dates.id_feature,
        id_agent = dates.id_agent,
        params = params_json
    )

    db.add(addactive)
    db.commit()
    db.refresh(addactive)
    return addactive

def delete_active_default(db:Session, dates:schemas.Manageable):
    db_active = db.query(models.Active_default).filter( and_(models.Active_default.id_feature == dates.id_feature,models.Active_default.id_agent == dates.id_agent ) ).first()
    #print(f'{db_active.id_active} ::::: {db_active.id_feature} ::::::: {db_active.id_agent}')

    if db_active:
         db.delete(db_active)
         db.commit()
         return "tarea eliminada"
    return "Esta tarea ya fue cancelada o no es posible"