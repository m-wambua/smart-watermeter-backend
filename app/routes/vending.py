from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session 
from app.core.database import get_db
from app.services.vending_services import vend_meter

from app.schemas.vending_schema import VendedToken

router=APIRouter(prefix="/api/vending", tags=['Vending'])
@router.post("/generate", response_model=VendedToken)
def generate_vending_token( 
                           meter_number:str,
                           phone_number:str,
                           amount:float,
                           db:Session=Depends(get_db)):
    """Simulate vending process and return token info"""
    token_data=vend_meter(db,meter_number,phone_number,amount)
    return token_data