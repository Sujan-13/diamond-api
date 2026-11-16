from pydantic import BaseModel, Field
from typing import Literal

class Diamond(BaseModel):
    carat:float = Field(ge=0.15,le=6)
    color:Literal['E', 'I', 'J', 'H', 'F', 'G', 'D']
    clarity:Literal['SI2', 'SI1', 'VS1', 'VS2', 'VVS2', 'VVS1', 'I1', 'IF']
    depth:float = Field(ge=35,le=90)
    table:float = Field(ge=35,le=110)
    price:float = Field(ge=250,le=20000)
    x:float = Field(ge=3,le=15)
    y:float = Field(ge=3,le=70)
    z:float = Field(ge=0.5,le=50)

class PredictionOutput(BaseModel):
    cut:Literal['Fair', 'Good', 'Very Good', 'Premium', 'Ideal']
    probability:float


