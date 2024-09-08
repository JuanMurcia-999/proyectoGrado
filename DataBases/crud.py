from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
import models, schemas
import json
from datetime import datetime


Ag = models.Agents
Af = models.Administered_features
Ad = models.Active_default
Hf = models.History_features
Df =models.Default_features
Al = models.Alarms
Ts = models.Traps
# Peticion que retorna todos los agentes en la base de datos

# -------------------------------------------------------------------------------------------AGENTS


def get_all_agent(db: Session):
    return db.query(Ag).options(joinedload(Ag.type)).all()



# Query para creacion de Agentes
def create_agent(db: Session, agent: schemas.CreateAgent):
    try:
        db_agent = Ag(
            ag_name=agent.ag_name, ip_address=agent.ip_address, ag_type=agent.ag_type
        )

        db.add(db_agent)
        db.commit()
        db.refresh(db_agent)
        return db_agent.id_agent
    except Exception:
        return False
    finally:
        db.close()


# Query para eleiminacion de agentes
def delete_agent(db: Session, field, value):
    try:
        db_agent = (
            db.query(Ag)
            .filter(getattr(Ag, field) == value)
            .first()
        )
        if db_agent:
            db.delete(db_agent)
            db.commit()
            return db_agent
    except Exception:
        return False
    finally:
        print("operacion terminada")
        db.close()


# ------------------------------------------------------------------------------------------------FEATURES


# Query para obtener todas las caracteristicas que son monitoreadas
def get_all_features(db: Session):
    return (
        db.query(Af)
        .options(joinedload(Af.agent))
        .all()
    )


# Query para obtener todas las caracteristicas segun agente
def get_all_features_agent(db: Session, value):
    return (
        db.query(Af)
        .filter(Af.id_agent == value)
        .options(joinedload(Af.agent))
    )


# Agregar una nueva feature a monitorizar
def new_feature(db: Session, feature: schemas.new_features):
    try:
        db_agent = Af(
            id_adminis=feature.id_adminis,
            id_sensor=feature.id_sensor,
            id_agent=feature.id_agent,
            oid=feature.oid,
            adminis_name=feature.adminis_name,
            timer=feature.timer,
        )

        db.add(db_agent)
        db.commit()
        db.refresh(db_agent)
        return True
    except Exception:
        return False
    finally:
        db.close()


# Query para eleiminacion de features
def delete_feature(db: Session, id):
    db_agent = (
        db.query(Af)
        .filter(Af.id_adminis == id)
        .first()
    )
    if db_agent:
        db.delete(db_agent)
        db.commit()
        return True
    return True


def delete_active_default(db: Session, dates: schemas.Manageable):
    db_active = (
        db.query(Ad)
        .filter(
            and_(
                Ad.id_feature == dates.id_feature,
                Ad.id_agent == dates.id_agent,
            )
        )
        .first()
    )
    # print(f'{db_active.id_active} ::::: {db_active.id_feature} ::::::: {db_active.id_agent}')

    if db_active:
        db.delete(db_active)
        db.commit()
        return "tarea eliminada"
    return "Esta tarea ya fue cancelada o no es posible"


# ---------------------------------------------------------------------------------------------HISTORY

def get_history_sensor(db: Session, filter: schemas.getHistory):

    if filter.id_sensor is None:
        condition = filter.id_adminis
        column = "id_adminis"
    else:
        condition = filter.id_sensor
        column = "id_sensor"

    response = db.query(
        Hf.value, Hf.time
    ).filter(
        Hf.id_adminis == condition,
        Hf.id_agent == filter.id_agent,
    )
    namesensor = (
        db.query(Af.adminis_name)
        .filter(getattr(Af, column) == condition)
        .all()
    )

    name = namesensor[0][0]
    values = [item[0] for item in response]
    date = [item[1].strftime("%H:%M:%S") for item in response]

    return {"value": {name: values}, "created_at": date}


# Modelo de respuesta par las interfaces


def get_history_Network(db: Session, filter: schemas.getHistory):
    IN = (
        db.query(Hf.value, Hf.date)
        .filter(
            Hf.id_adminis == 1001,
            Hf.id_agent == filter.id_agent,
        )
        .order_by(Hf.id_register.desc())
    )
    OUT = (
        db.query(Hf.value, Hf.date)
        .filter(
            Hf.id_adminis == 1002,
            Hf.id_agent == filter.id_agent,
        )
        .order_by(Hf.id_register.desc())
    )

    valuesIN = [item[0] for item in IN]
    valuesOUT = [item[0] for item in OUT]
    date = [item[1].strftime("%Y-%m-%d") for item in IN]

    return {"value": {"valuesIN": valuesIN, "valuesOUT": valuesOUT}, "created_at": date}




######################################   FILTRADO DE DATOS
def get_history_filter(db: Session, filter: schemas.filterHistory):

    if filter.id_sensor is None:
        condition = filter.id_adminis
        column = "id_adminis"
    else:
        condition = filter.id_sensor
        column = "id_sensor"

 
   
    try:
        response = (
            db.query(Hf.value, Hf.time, Hf.date)
            .filter(
                and_(
                    Hf.id_agent == filter.id_agent,
                    Hf.id_adminis == condition,
                    Hf.date == func.date(filter.datebase, filter.daterange),
                    Hf.time >= func.time("00:00:00", filter.timerange),
                )
            )
            .order_by(Hf.date.asc())
            .limit(filter.limit)
            .offset(filter.offset)
            .all()
        )

        namesensor = (
            db.query(Af.adminis_name)
            .filter(getattr(Af, column) == condition)
            .first()
        )

        if response:

            name = namesensor.adminis_name
            values = [item.value for item in response]
            time = [item.time.strftime("%H:%M:%S") for item in response]
            date = [item.date.strftime("%Y-%m-%d") for item in response]

            minimum = min(values)
            maximus = max(values)
            average = sum(values) / len(values)

            response_json = {
                "data": {
                    "datagrafic": [
                        {
                            "name": name,
                            "values": values,
                            "date": date,
                            "time": time,
                            "stadistics": {
                                "min": minimum,
                                "max": maximus,
                                "avg": average,
                            },
                        }
                    ],
                },
            }

            return response_json
        else:
            return {
                "data": {
                    "datagrafic": [
                        {
                            "name": 'Sin datos',
                            "values": [],
                            "date": [],
                            "time": [],
                            "stadistics": {
                                "min": 0,
                                "max": 0,
                                "avg": 0,
                            },
                        }
                    ],
                },
            }

    except Exception:
        return False
    finally:
        db.close()


####################################################################################
# Agregar un nuevo registro al historial
def add_history(db: Session, record: schemas.addHistory):

    db_history = Hf(
        id_agent=record.id_agent, id_adminis=record.id_adminis, value=record.value
    )

    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    db.close()
    return db_history


# ----------------------------------------------------------------------------------------GESTIONABLES


def get_default_features_agent(db: Session, id, type):
    if type == 4:
        types=[4,2]
    else:
        types = [type]
    return (
        db.query(Df.fe_name, Df.id_feature)
        .outerjoin(
            Ad,
            and_(
                Df.id_feature == Ad.id_feature,
                Ad.id_agent == id,
            ),
        )
        .filter(
            and_(
                Ad.id_feature.is_(None),
                Df.id_type.in_([1, *types]),
                Df.id_feature != 100,
            )
        )
    )


def get_active_default(db: Session, id, type):
    if type == 4:
        types=[4,2]
    else:
        types = [type]
    return (
        db.query(Df.fe_name, Df.id_feature)
        .join(
            Ad,
            Df.id_feature == Ad.id_feature,
        )
        .filter(
            and_(
                Ad.id_agent == id,
                Df.id_type.in_([1, *types]),
                Ad.id_feature != 100,
            )
        )
    )


def add_active_default(db: Session, dates: schemas.Manageable):
    params_json = json.dumps(dates.params)
    addactive = Ad(
        id_feature=dates.id_feature, id_agent=dates.id_agent, params=params_json
    )

    db.add(addactive)
    db.commit()
    db.refresh(addactive)
    db.close()
    return addactive


def delete_feature_two(db: Session, name, id):
    print(name)
    print(id)
    db_feature = (
        db.query(Af)
        .filter(
            and_(
                Af.adminis_name.like(f"{name}%"),
                Af.id_agent == id,
            )
        )
        .all()
    )

    if db_feature:
        for feature in db_feature:
            db.delete(feature)
        db.commit()
        return True
    return False


# ------------------------------------------------------------------------------------ ALARMAS
def get_alarm(db: Session, id_agent):
    try:
        return db.query(Al).filter(Al.id_agent == id_agent).all()
    except Exception:
        return False


def delete_alarm(db: Session, id_alarm):
    db_alarm = (
        db.query(Al).filter(Al.id_alarm == id_alarm).first()
    )

    if db_alarm:
        db.delete(db_alarm)
        db.commit()
        return True
    else:
        return False


def add_alarm(db: Session, alarm: schemas.newAlarm):
    try:
        addalarm = Al(
            id_agent=alarm.id_agent,
            id_adminis=alarm.id_adminis,
            id_sensor=alarm.id_sensor,
            operation=alarm.operation,
            value=alarm.value,
        )

        db.add(addalarm)
        db.commit()
        db.refresh(addalarm)
        db.close()
        return True
    except Exception:
        return False


# ------------------------------------------------------------TRAPS

def get_all_traps(db: Session):
    return db.query(Ts).all()

def get_trap_message(value ,db: Session):
    
    valor=db.query(Ts.message).filter(Ts.id_alarm == value).first()
    return valor[0]
