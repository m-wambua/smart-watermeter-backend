from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.core.database import Base
from sqlalchemy.orm import relationship
class MpesaTransaction(Base):
    __tablename__ = "mpesa_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_type = Column(String(50))
    trans_id = Column(String(50), unique=True)
    trans_time = Column(String(50))
    trans_amount = Column(Float)
    business_short_code = Column(String(20))
    bill_ref_number = Column(String(50))
    invoice_number = Column(String(50), nullable=True)
    org_account_balance = Column(String(50), nullable=True)
    third_party_trans_id = Column(String(50), nullable=True)
    msisdn = Column(String(20))
    first_name = Column(String(50))
    middle_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    vended_tokens = relationship("VenderToken", back_populates="payment", lazy="joined")

