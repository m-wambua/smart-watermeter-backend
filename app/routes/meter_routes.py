from fastapi import APIRouter,Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.meter import MeterAggregare
from app.utils.logger import get_logger

router=APIRouter(prefix="/api/meter", tags=['Meter'])
logger=get_logger("MeterRoutes")

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.get("/{meter_number}/aggregate")
def get_meter_aggregate(meter_number:str,db:Session=Depends(get_db)):
    agg=db.query(MeterAggregare).filter(MeterAggregare.meter_number==meter_number).first()
    if not agg:
        raise HTTPException(status_code=404,detail="Meter not found")
    return {
        "meter_number":agg.meter_number,
        "last_entered_units":agg.last_entered_units,
        "last_update_at":agg.last_update_at,
        "last_entered_amount":agg.last_entered_amount,
        "last_payer":agg.last_payer,
        "total_dispensed_units":agg.total_dispensed_units,
        "total_token_count":agg.total_token_count,
        "last_token_time":agg.last_token_time,
        "total_amount_paid":agg.total_amount_paid,
        "total_payment_count":agg.total_payment_count,
        "last_payment_time":agg.last_payment_time
    }