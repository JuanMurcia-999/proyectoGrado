from pydantic import BaseModel,Field
from typing import Any
from datetime import datetime, date, time
class getHistory(BaseModel):
    id_agent: int
    id_sensor: int | None
    id_adminis: int

class filterHistory(BaseModel):
    id_agent: int | Any
    id_adminis: int | Any
    id_sensor: int | Any
    datebase: str | Any
    timebase: str | Any
    daterange: str | Any
    timerange: str | Any
    limit: int | Any
    offset: int | Any

class addHistory(BaseModel):
    id_agent: int
    id_adminis: int
    value: Any
    Date: date | str = Field(default_factory=lambda: datetime.now().date().strftime("%Y-%m-%d"))
    Time: time | str = Field(default_factory=lambda: datetime.now().time().strftime("%H:%M:%S"))
