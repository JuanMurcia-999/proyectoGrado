from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
import models,schemas
import json

# Peticion que retorna todos los agentes en la base de datos

# -------------------------------------------------------------------------------------------AGENTS

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
    db.close()
    return db_agent

#Query para eleiminacion de agentes
def delete_agent(db: Session, field,value):
    db_agent = db.query(models.Agents).filter( getattr(models.Agents,field) == value).first()
    if db_agent:
        db.delete(db_agent)
        db.commit()
        db.close()
        return "agente eliminado"
    return "Este agente ya fue eliminado o no existe"




#------------------------------------------------------------------------------------------------FEATURES




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
    id_adminis=feature.id_adminis,
    id_agent=feature.id_agent, 
    oid= feature.oid, 
    adminis_name = feature.adminis_name,
    timer=feature.timer)

    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

#Query para eleiminacion de features
def delete_feature(db: Session,id):
    db_agent = db.query(models.Administered_features).filter(models.Administered_features.id_adminis == id).first()
    if db_agent:
        db.delete(db_agent)
        db.commit()
        return True
    return True


def delete_active_default(db:Session, dates:schemas.Manageable):
    db_active = db.query(models.Active_default).filter( and_(models.Active_default.id_feature == dates.id_feature,models.Active_default.id_agent == dates.id_agent ) ).first()
    #print(f'{db_active.id_active} ::::: {db_active.id_feature} ::::::: {db_active.id_agent}')

    if db_active:
         db.delete(db_active)
         db.commit()
         return "tarea eliminada"
    return "Esta tarea ya fue cancelada o no es posible"

# ---------------------------------------------------------------------------------------------HISTORY

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


# Agregar un nuevo registro al historial
def add_history(db:Session, record: schemas.addHistory):

    db_history= models.History_features  (
        id_agent=record.id_agent,
        id_adminis=record.id_adminis,
        value=record.value
        )

    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    db.close()
    return db_history


#----------------------------------------------------------------------------------------GESTIONABLES




def get_default_features_agent(db: Session,id,type):
    return db.query(models.Default_features.fe_name,models.Default_features.id_feature).outerjoin(
         models.Active_default,
         and_(
          models.Default_features.id_feature == models.Active_default.id_feature,
          models.Active_default.id_agent == id
          )).filter(
                and_(
                    models.Active_default.id_feature.is_(None) ,
                    models.Default_features.id_type.in_([1,type]),
                    models.Default_features.id_feature != 100
                ))


def get_active_default(db:Session,id,type):
    return db.query(models.Default_features.fe_name,models.Default_features.id_feature).join(
         models.Active_default,
          models.Default_features.id_feature == models.Active_default.id_feature).filter(
                and_(
                    models.Active_default.id_agent == id,
                    models.Default_features.id_type.in_([1,type]),
                    models.Active_default.id_feature != 100,  
                ))



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
    db.close()
    return addactive


def delete_feature_two(db:Session, dates:schemas.Manageable):
    db_active = db.query(models.Active_default).filter( and_(models.Active_default.id_feature == dates.id_feature,models.Active_default.id_agent == dates.id_agent ) ).first()
    #print(f'{db_active.id_active} ::::: {db_active.id_feature} ::::::: {db_active.id_agent}')

    if db_active:
         db.delete(db_active)
         db.commit()
         return "tarea eliminada"
    return "Esta tarea ya fue cancelada o no es posible"

def delete_feature_two(db: Session,name,id):
    db_agent = db.query(models.Administered_features).filter( and_(models.Administered_features.adminis_name == name,
                                                                   models.Administered_features.id_agent == id )).first()
    
    print(f'{db_agent.id_agent}:::::::: {db_agent.adminis_name}')
    if db_agent:
        db.delete(db_agent)
        db.commit()
        return True
    return False  