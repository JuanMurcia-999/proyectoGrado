from pydantic import BaseModel


class ConfigAnchoBanda(BaseModel):
    ip: str
    Num_Interface: str
    intervalo: int | None
    id_adminis: int
    id: int

    class Config:
        arbitrary_types_allowed = True


class ConfigProcesses(BaseModel):
    ip: str
    timer: int | None
    id_adminis: int
    id: int

    class Config:
        arbitrary_types_allowed = True

