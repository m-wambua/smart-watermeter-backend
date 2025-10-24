from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.aggregate_service import get_home_aggregate
from app.services.aggregate_service import get_all_home_aggregates as fetch_home_data


router=APIRouter(prefix="/api/aggregate", tags=['Aggregate'])
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.get("/home/{meter_number}")
def get_home_page_data(meter_number:str, db:Session=Depends(get_db)):
    data=get_home_aggregate(db,meter_number)
    if not data:
        raise HTTPException(status_code=404, detail="Data not found")
    return data

@router.get("/home")
def get_all_home_data(db:Session=Depends(get_db)):
    data=fetch_home_data(db)
    return data