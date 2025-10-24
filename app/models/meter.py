from sqlalchemy import Column, Integer,String,Float,DateTime, func 
from sqlalchemy.ext.declarative import declarative_base
from app.core.database import Base 

class Meter(Base):
    __tablename__="meters"
    id=Column(Integer,primary_key=True,index=True)
    meter_number=Column(String, unique=True, nullable=False)
    customer_name=Column(String,nullable=True)
    phone_number=Column(String, nullable=True)
    email=Column(String, nullable=True)
    created_at=Column(DateTime,server_default=func.now())
    
    
class MeterAggregare(Base):
    __tablename__="meter_aggregates"
    id=Column(Integer,primary_key=True,index=True)
    meter_number=Column(String,unique=True,nullable=False, index=True)
    last_entered_units=Column(Float, nullable=True)
    last_update_at=Column(DateTime,nullable=True)
    last_entered_amount=Column(Float,nullable=True)
    last_payer=Column(String,nullable=True)
    
    
    
    total_dispensed_units=Column(Float,nullable=False,default=0.0)
    total_token_count=Column(Integer,nullable=False,default=0)
    last_token_time=Column(DateTime,nullable=True)
    total_amount_paid=Column(Float,nullable=False,default=0.0)
    total_payment_count=Column(Integer,nullable=False,default=0)
    last_payment_time=Column(DateTime,nullable=True)
    
    
    updated_at=Column(DateTime,server_default=func.now(), onupdate=func.now())