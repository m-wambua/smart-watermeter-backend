from pydantic import BaseModel
from datetime import datetime


class VendedTokenbase(BaseModel):
    meter_number:str 
    amount:float 
    units:float
    token:str
    phone_number:str 
    
class VendedTokenCreate(VendedTokenbase):
    pass

class VendedToken(VendedTokenbase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True
