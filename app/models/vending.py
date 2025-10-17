from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class VenderToken(Base):
    __tablename__ = "vending_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    meter_number = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    units = Column(Float, nullable=False)
    token = Column(String, unique=True, nullable=False)
    phone_number = Column(String, nullable=False)
    payment_id = Column(Integer, ForeignKey("mpesa_transactions.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    payment = relationship("MpesaTransaction", back_populates="vended_tokens", lazy="joined")
