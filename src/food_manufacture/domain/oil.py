from enum import Enum
from typing import NewType

from pydantic import BaseModel

OilName = NewType("OilName", str)


class OilType(Enum):
    VEGETABLE = "VEGETABLE"
    NON_VEGETABLE = "NON_VEGETABLE"

    @classmethod
    def names(cls) -> list[str]:
        return [t.name for t in cls]


class Oil(BaseModel):
    name: OilName
    oil_type: OilType
    hardness: float
