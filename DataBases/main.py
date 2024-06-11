from fastapi import Depends,FastAPI,HTTPException
from sqlalchemy.orm import Session

import crud,models,schemas
from database import SessionLocal,engine


models.Base.metadata.create_all(bind=engine)  # crea la base de datos si no existe

app = FastAPI()



def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()




@app.get("/agents/all/",response_model=list[schemas.Agent])
def read_agents(db:Session=Depends(get_db)):
    agents = crud.get_all_agent(db=db)
    return agents

@app.post("/agents/create/",response_model=schemas.Agent)
def create_agent(agent: schemas.CreateAgent, db:Session=Depends(get_db)):
    return crud.create_agent(db=db, agent=agent)

@app.delete("/agents/delete/{field}") 
def delete_agent(field:models.ModelField,value, db:Session=Depends(get_db)):
    return crud.delete_agent(db=db, field=field.name,value=value)



