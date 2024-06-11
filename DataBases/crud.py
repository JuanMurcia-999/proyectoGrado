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



