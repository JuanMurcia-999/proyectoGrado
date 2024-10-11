from pydantic import BaseModel
from ..schema.agents_schemas import Agent


class new_features(BaseModel):
    id_adminis: int | None
    id_sensor: int | None
    ag_name: str
    id_agent: int
    oid: str
    adminis_name: str
    timer: int


class features(BaseModel):
    id_agent: int
    oid: str
    adminis_name: str
    timer: int

    class config:
        from_attributes = True


class Features(features):
    id_adminis: int | None
    id_sensor: int | None

    class config:
        from_attributes = True


# lectura de features con agentes
class FeatureswithAgent(Features):
    agent: Agent

    class Config:
        from_attributes = True
