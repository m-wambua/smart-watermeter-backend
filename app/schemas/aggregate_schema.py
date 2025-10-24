from pydantic import BaseModel
from datetime import datetime
from typing import Optional
class HomeAggregateResponse(BaseModel):
    meter_number:str 
    last_units:float 
    last_update:Optional[datetime]
    last_amount:float 
    last_phone_number:Optional[str]
    
    class Config:
        orm_mode = True