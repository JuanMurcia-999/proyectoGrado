from pydantic import BaseModel
from typing import Dict,Any


class stoptask(BaseModel):
    name: str
    nametask: str
    id_agent: int
    id_feature: int

class ReadDefaultFeature(BaseModel):
    id_feature: int
    fe_name: str


class Manageable(stoptask):
    params: Dict[str, Any]


class new_features(BaseModel):
    id_adminis: int | None
    id_sensor: int | None
    ag_name: str
    id_agent: int
    oid: str
    adminis_name: str
    timer: int