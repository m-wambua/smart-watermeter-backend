from pydantic import BaseModel
from typing import Optional

class MpesaTransactionCreate(BaseModel):
    TransactionType: str
    TransID: str
    TransTime: str
    TransAmount: float
    BusinessShortCode: str
    BillRefNumber: str
    MSISDN: str
    FirstName: Optional[str]
    MiddleName: Optional[str]
    LastName: Optional[str]

class MpesaTransactionResponse(BaseModel):
    ResultCode: int
    ResultDesc: str
