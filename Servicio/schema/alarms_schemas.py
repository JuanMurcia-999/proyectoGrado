from pydantic import BaseModel

class newAlarm(BaseModel):

    id_agent: int
    id_adminis: int
    id_sensor: int | None
    operation: str
    value: float
    counter: int | None


class readAlarm(newAlarm):
    id_alarm: int