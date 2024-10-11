from pydantic import BaseModel
from typing import Any

class elements(BaseModel):
    ID: int
    IP: str
    TIMES: list[int]
    OIDS: list[list[str]]
    IDF: list[list[int]]

class taskoid(BaseModel):
    TIME: int
    OIDS: list[Any]
    ID: int
    IDF: list[int]
    IP: str
