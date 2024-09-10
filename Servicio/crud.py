from sqlalchemy.orm import joinedload
from sqlalchemy import or_, and_, func
import models, schemas
import json
from database import get_db

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


Ag = models.Agents
Af = models.Administered_features
Ad = models.Active_default
Hf = models.History_features
Df = models.Default_features
Al = models.Alarms


# # Peticion que retorna todos los agentes en la base de datos
# -------------------------------------------------------------------------------------------AGENTS


# Obtener todos los agentes
async def get_all_agent(db: AsyncSession):
    result = await db.execute(select(Ag).options(selectinload(Ag.type)))
    return result.scalars().all()


# Crear un agente
async def create_agent(db: AsyncSession, agent: schemas.CreateAgent):
    try:
        db_agent = Ag(
            ag_name=agent.ag_name,
            ip_address=agent.ip_address,
            ag_type=agent.ag_type,
        )

        db.add(db_agent)
        await db.commit()  
        await db.refresh(db_agent)  
        return db_agent.id_agent
    except Exception as e:
        print(f"Error: {e}") 
        return False


# Eliminar un agente
async def delete_agent(db: AsyncSession, field, value):
    try:
        result = await db.execute(select(Ag).filter(getattr(Ag, field) == value))
        db_agent = result.scalars().first()
        if db_agent:
            await db.delete(db_agent)  
            await db.commit()  
            return db_agent
    except Exception as e:
        print(f"Error: {e}")  
        return False
    finally:
        print("Operación terminada")


# ------------------------------------------------------------------------------------------------FEATURES


# Query para obtener todas las caracteristicas que son monitoreadas
async def get_all_features(db: AsyncSession):
    result = await db.execute(select(Af).options(joinedload(Af.agent)))
    return result.scalars().all()


# Query para obtener todas las caracteristicas segun agente
async def get_all_features_agent(db: AsyncSession, value):
    result = await db.execute(
        select(Af).filter(Af.id_agent == value).options(joinedload(Af.agent))
    )
    return result.scalars().all()


# Agregar una nueva feature a monitorizar
async def new_feature(db: AsyncSession, feature: schemas.new_features):
    try:
        db_feature = Af(
            id_adminis=feature.id_adminis,
            id_sensor=feature.id_sensor,
            id_agent=feature.id_agent,
            oid=feature.oid,
            adminis_name=feature.adminis_name,
            timer=feature.timer,
        )

        db.add(db_feature)
        await db.commit()
        await db.refresh(db_feature)
        return True
    except Exception:
        return False



# Query para eleiminacion de features
async def delete_feature(db: AsyncSession, id):
    try:
        # Ejecutar la consulta y esperar el resultado
        result = await db.execute(select(Af).filter(Af.id_adminis == id))
        db_feature = (
            result.scalar_one_or_none()
        )

        if db_feature:
            await db.delete(db_feature)
            await db.commit()
            return True
    except Exception:
        return False


async def delete_active_default(db: AsyncSession, dates: schemas.Manageable):
    result = await db.execute(
        select(Ad).filter(
            and_(
                Ad.id_feature == dates.id_feature,
                Ad.id_agent == dates.id_agent,
            )
        )
    )
    db_active = result.scalars().first()

    if db_active:
        await db.delete(db_active)
        await db.commit()
        return "tarea eliminada"
    return "Esta tarea ya fue cancelada o no es posible"


# ---------------------------------------------------------------------------------------------HISTORY


async def get_history_sensor(db: AsyncSession, filter: schemas.getHistory):
    if filter.id_sensor is None:
        condition = filter.id_adminis
        column = "id_adminis"
    else:
        condition = filter.id_sensor
        column = "id_sensor"

   
    result = await db.execute(
        select(Hf.value, Hf.time).filter(
            Hf.id_adminis == condition,
            Hf.id_agent == filter.id_agent,
        )
    )
    response = result.fetchall()

    
    result_namesensor = await db.execute(
        select(Af.adminis_name).filter(getattr(Af, column) == condition)
    )
    namesensor = result_namesensor.fetchall()

    if not namesensor:
        return {"error": "No se encontró el sensor"}

    name = namesensor[0][0]
    values = [item[0] for item in response]
    date = [item[1].strftime("%H:%M:%S") for item in response]

    return {"value": {name: values}, "created_at": date}




async def get_history_Network(db: AsyncSession, filter: schemas.getHistory):
    
    result_in = await db.execute(
        select(Hf.value, Hf.date)
        .filter(
            Hf.id_adminis == 1001,
            Hf.id_agent == filter.id_agent,
        )
        .order_by(Hf.id_register.desc())
    )
    IN = result_in.fetchall()

   
    result_out = await db.execute(
        select(Hf.value, Hf.date)
        .filter(
            Hf.id_adminis == 1002,
            Hf.id_agent == filter.id_agent,
        )
        .order_by(Hf.id_register.desc())
    )
    OUT = result_out.fetchall()

    
    valuesIN = [item[0] for item in IN]
    valuesOUT = [item[0] for item in OUT]
    date = [item[1].strftime("%Y-%m-%d") for item in IN]

    return {"value": {"valuesIN": valuesIN, "valuesOUT": valuesOUT}, "created_at": date}


########################################################################333   FILTRADO DE DATOS

Faile = {
                "data": {
                    "datagrafic": [
                        {
                            "name": "Sin datos",
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

async def get_history_filter(db: AsyncSession, filter: schemas.filterHistory):
    if filter.id_sensor is None:
        condition = filter.id_adminis
        column = "id_adminis"
    else:
        condition = filter.id_sensor
        column = "id_sensor"

    try:
       
        result = await db.execute(
            select(Hf.value, Hf.time, Hf.date)
            .filter(and_(Hf.id_agent == filter.id_agent, Hf.id_adminis == condition))
            .order_by(Hf.date.asc())
            .limit(filter.limit)
            .offset(filter.offset)
        )
        response = result.fetchall()
       
        name_result = await db.execute(
            select(Af.adminis_name).filter(getattr(Af, column) == condition)
        )
        # print(name_result.first().adminis_name)
        namesensor = name_result.scalar_one_or_none()
        if response != [] and name_result != None:
            values = [item.value for item in response]
            time = [item.time.strftime("%H:%M:%S") for item in response]
            date = [item.date.strftime("%Y-%m-%d") for item in response]

            minimum = min(values)
            maximus = max(values)
            average = sum(values) / len(values)

            return {
                "data": {
                    "datagrafic": [
                        {
                            "name": namesensor,
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
        else:
            return Faile
    except Exception as e:

        return Faile


####################################################################################
# Agregar un nuevo registro al historial
async def add_history(data):
    async for db in get_db():
        try:
                async for db in get_db():
                    db_history = models.History_features(
                        id_agent=data.id_agent,
                        id_adminis=data.id_adminis,
                        value=data.value,
                    )

                    db.add(db_history)
                    await db.commit()
                    await db.refresh(db_history)
                    return True
        except Exception :
                print("algo paso add_history")
                return False

        


# ----------------------------------------------------------------------------------------GESTIONABLES


async def get_default_features_agent(db: AsyncSession, id, type):
    result = await db.execute(
        select(Df.fe_name, Df.id_feature)
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
                Df.id_type.in_([1, type]),
                Df.id_feature != 100,
            )
        )
    )

    return result.all()


async def get_active_default(db: AsyncSession, id, type):
    result = await db.execute(
        select(Df.fe_name, Df.id_feature)
        .join(
            Ad,
            Df.id_feature == Ad.id_feature,
        )
        .filter(
            and_(
                Ad.id_agent == id,
                Df.id_type.in_([1, type]),
                Ad.id_feature != 100,
            )
        )
    )

    return result.all()


async def add_active_default(db: AsyncSession, dates: schemas.Manageable):
    result = await db.execute(
        select(Ad).filter(
            and_(Ad.id_agent == dates.id_agent, Ad.id_feature == dates.id_feature)
        )
    )
    if result:
        print("ya existe")
    else:
        print("agregado")
    try:
        params_json = json.dumps(dates.params)
        addactive = Ad(
            id_feature=dates.id_feature, id_agent=dates.id_agent, params=params_json
        )

        db.add(addactive)
        await db.commit()  
        await db.refresh(addactive)
        print(addactive) 
        return addactive
    except Exception:
        print("fallo e add_active_Default")
        return False


async def delete_feature_two(db: AsyncSession, name, id):
    print(name)
    print(id)

    result = await db.execute(
        select(Af).filter(
            and_(
                Af.adminis_name.like(f"{name}%"),
                Af.id_agent == id,
            )
        )
    )

    db_feature = result.scalars().all()  #

    if db_feature:
        for feature in db_feature:
            await db.delete(feature) 
        await db.commit() 
        return True
    return False


# ------------------------------------------------------------------------------------ ALARMAS
async def get_alarm(db: AsyncSession, id_agent):
    try:
        result = await db.execute(select(Al).filter(Al.id_agent == id_agent))
        return result.scalars().all()  
    except Exception:
        return False


async def delete_alarm(db: AsyncSession, id_alarm):
    db_alarm = await db.execute(select(Al).filter(Al.id_alarm == id_alarm))

    db_alarm_instance = (
        db_alarm.scalar_one_or_none()
    )  

    if db_alarm_instance:
        await db.delete(db_alarm_instance)  
        await db.commit()  
        return True
    else:
        return False


async def add_alarm(db: AsyncSession, alarm: schemas.newAlarm):
    try:
        addalarm = Al(
            id_agent=alarm.id_agent,
            id_adminis=alarm.id_adminis,
            id_sensor=alarm.id_sensor,
            operation=alarm.operation,
            value=alarm.value,
        )

        db.add(addalarm)
        await db.commit() 
        await db.refresh(addalarm)  

        return True
    except Exception:
        return False


# ---------------------------------------------------- de ColaAlarms


async def get_administered_feature(column: str, tarea):
    async for db in get_db():
        try:
            query = await db.execute(
                select(models.Administered_features).filter(
                    getattr(models.Administered_features, column) == tarea.id_adminis
                )
            )
            return query.scalars().first()
        except Exception:
            print("fallo en get_administered_feature")


async def get_alarms(column: str, data):
    async for db in get_db():
        try:
            stmt = (
                select(models.Alarms)
                .join(
                    models.Administered_features,
                    models.Alarms.id_adminis == models.Administered_features.id_adminis,
                )
                .filter(
                    and_(
                        getattr(models.Administered_features, column)
                        == data.id_adminis,
                        models.Administered_features.id_agent == data.id_agent,
                    )
                )
            )

            result = await db.execute(stmt)
            return result.scalars().first()
        except Exception:
            print("fallo en get_alarms")


# --------------------------------------------------------------------- procesos de los demas modeulos

# taskoid


async def get_unique_times(id_agent):
    async for db in get_db():
        try:
            return (
                (
                    await db.execute(
                        select(Af.timer)
                        .filter(
                            Af.id_agent == id_agent,
                            Af.oid != "",
                        )
                        .distinct()
                    )
                )
                .scalars()
                .all()
            )
        except Exception as e:
            print(e)


async def get_features_oid(inter, id_agent):
    async for db in get_db():
        try:
            return (
                await db.execute(
                    select(Af.oid, Af.id_adminis).filter(
                        Af.timer == f"{inter}",
                        Af.id_agent == id_agent,
                        Af.oid != "",
                    )
                )
            ).all()
        except Exception:
            print("fallo en get_features")


# --------------------------------------------------------------------------- main

async def get_sensors_startup(id):
    async for db in get_db():
        try:
            return (
                (
                    await db.execute(
                        select(models.Active_default)
                        .options(joinedload(models.Active_default.features))
                        .filter(models.Active_default.id_agent == id)
                    )
                )
                .scalars()
                .all()
            )
        
        except Exception:
            print('fallo en get_sensors_startup')

# -----------------------------------------------------------------------Abstracciones

async def get_A_cpu(date):
    async for db in get_db():
        try:
            return(await db.execute(
                select(Hf.id_adminis).filter(Hf.id_adminis.like(f"{date}%")).distinct()
            )).scalars().all()
        except  Exception:
            print('fallo get_A_cpu')


async def get_B_cpu(filter:schemas.filterHistory):
    async for db in get_db():
        try:
           return (await db.execute(
                    select(Hf.value, Hf.time, Hf.date)
                    .filter(
                        and_(
                            Hf.id_agent == filter.id_agent,
                            Hf.id_adminis == id
                        )
                    )
                    .order_by(Hf.date.asc())
                    .limit(filter.limit)
                    .offset(filter.offset)
                )).all()
            
        except Exception:
            print('fallo get_B_cpu')

async def get_B_network(filter:schemas.filterHistory, ids):
    async for db in get_db():
        try:
            return (await db.execute(
                select(Hf.value, Hf.time, Hf.date)
                .filter(
                    and_(
                        Hf.id_agent == filter.id_agent,
                        Hf.id_adminis.in_([ids["In"], ids["Out"]]),
                    )
                )
                .order_by(Hf.date.asc())
                .limit(filter.limit)
                .offset(filter.offset)
            )).all()
        except Exception:
            print('fallo get_B_network')

