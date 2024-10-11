from pydantic import BaseModel


class CreateAgent(BaseModel):
    ag_name: str | None
    ip_address: str | None
    ag_type: int | None

class Agent(CreateAgent):
    id_agent: int | None

    class Config:
        from_attributes = True



class Agent(CreateAgent):
    id_agent: int | None

    class Config:
        from_attributes = True
