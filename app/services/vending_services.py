import random
from sqlalchemy.orm import Session 
from app.models.vending import VenderToken

from app.schemas.vending_schema import VendedTokenCreate
from app.services.sms_service import SMSService
from app.services.sms_services import get_sms_service
from app.services.aggregate_service import update_on_vend



def generate_token_string()->str:
    """Simulate a token in (in the final implementation Hexing API will be added here)"""
    return ''.join([str(random.randint(0,9)) for _ in range(20)])

def compute_units(amount:float)->float:
    """Simple logic to convert amount to units"""
    rate_per_unit=10
    
    return round(amount/rate_per_unit,2)
def vend_meter(db:Session, meter_number:str, phone_number:str, amount:float):
    """Core vending logic: generate token, comoute units, store results"""
    units=compute_units(amount)
    token=generate_token_string()
    vended_data=VenderToken( 
                                  meter_number=meter_number,
                                  amount=amount,
                                  units=units,
                                  token=token,
                                  phone_number=phone_number)
    #vended_token=VenderToken(**vended_data.dict())
    db.add(vended_data)
    db.commit()
    db.refresh(vended_data)
    # ✅ Trigger SMS
    sms_service = SMSService(provider_name="mock")
    sms_service.send_token_sms(phone_number, token, units, meter_number)
    sms_service = get_sms_service()  # Uses mock by default
    message = (
        f"SmartWater Vending\n"
        f"Meter: {meter_number}\n"
        f"Units: {units}\n"
        f"Token: {token}\n"
        f"Thank you for using SmartWater!"
    )
    sms_service.send_sms(phone_number, message)
    
    
    update_on_vend(db,meter_number=vended_data.meter_number,
                   units=vended_data.units,
                   amount=vended_data.amount,
                   token=vended_data.token,
                   phone_number=vended_data.phone_number,
                   token_time=vended_data.timestamp)
    return vended_data