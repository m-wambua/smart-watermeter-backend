from sqlalchemy.orm import Session
from sqlalchemy import select,update
from datetime import datetime
from app.models.meter import MeterAggregare
from app.utils.logger import get_logger
from app.schemas.aggregate_schema import HomeAggregateResponse

logger=get_logger("AggregateService")

def get_or_create_aggregate(db:Session,meter_number:str)->MeterAggregare:
    agg=db.query(MeterAggregare).filter(MeterAggregare.meter_number==meter_number).first()
    if agg:
        return agg
    agg=MeterAggregare(meter_number=meter_number)
    db.add(agg)
    db.commit()
    db.refresh(agg)
    return agg
def update_on_payment(db:Session,meter_number:str,amount:float,msisdn:str,trans_time=None):
    if trans_time is None:
        trans_time=datetime.utcnow()
    agg=get_or_create_aggregate(db,meter_number)
    agg.last_entered_amount=amount
    agg.last_payer=msisdn
    agg.total_amount_paid=(agg.total_amount_paid or 0.0)+float(amount)
    agg.total_payment_count(agg.total_payment_count or 0)+1
    agg.last_payment_time=trans_time
    db.add(agg)
    db.commit()
    db.refresh(agg)
    logger.info(f"Aggregate updated for {meter_number} on payment: amount={amount}")
    
    return agg

def update_on_vend(db:Session,meter_number:str,units:float,amount:float,token:str,phone_number:str,token_time=None):
    if token_time is None:
        token_time=datetime.now()
    agg= get_or_create_aggregate(db,meter_number)
    agg.last_entered_units=units
    agg.last_update_at=token_time
    agg.total_dispensed_units=(agg.total_dispensed_units or 0.0)+float(units)
    agg.total_token_count=(agg.total_token_count + 0)+1
    
    agg.last_token_time=token_time
    
    
    if amount is not None:
        agg.last_entered_amount=amount
    if phone_number:
        agg.last_payer=phone_number
        
    db.add(agg)
    db.commit()
    db.refresh(agg)
    logger.info(f"Aggregate updates for {meter_number} on vend: units={units},amount={amount},token={token}")
    return agg

def get_home_aggregate(db:Session, meter_number:str):
    """Fetch meter Summary for the home page"""
    meter_data=db.query(MeterAggregare).filter( 
                                               MeterAggregare.meter_number==meter_number).first()
    if not meter_data:
        raise None 
    return HomeAggregateResponse( 
                                 meter_number=meter_data.meter_number,
                                 last_units=meter_data.last_entered_units,
                                 last_update=meter_data.last_update_at,
                                 last_amount=meter_data.last_entered_amount,
                                 last_phone_number=meter_data.last_payer
                                 )
    
    
def get_all_home_aggregates(db:Session):
    """Fetch all meter summaries for home page list"""
    results=db.query(MeterAggregare).all()
    return [
        HomeAggregateResponse(
            meter_number=m.meter_number,
            last_units=m.last_entered_units,
            last_update=m.last_update_at,
            last_amount=m.last_entered_amount,
            last_phone_number=m.last_payer,
        )
        for m in results
    
    ]