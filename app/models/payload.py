from pydantic import BaseModel


class PayloadModel(BaseModel):
    load: int
    fuels: dict[str, float]
    powerplants: list[dict]
