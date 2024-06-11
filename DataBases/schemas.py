from pydantic import BaseModel



#esquema de datos para los elementos de la tabla Agents



#Escritura
class CreateAgent(BaseModel):
    Hostname:str
    IP_address:str

#Lectura
class Agent(CreateAgent):
    ID_agent:int


