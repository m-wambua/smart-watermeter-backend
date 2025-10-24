# app/services/mpesa_transaction_service.py

from sqlalchemy.orm import Session
from app.models.payment import MpesaTransaction
from app.services.vending_services import vend_meter
from app.services.aggregate_service import update_on_payment
from app.utils.logger import get_logger

logger = get_logger("MpesaTransactionService")

def process_mpesa_transaction(db: Session, data: dict):
    """
    Process and store an M-Pesa C2B transaction.
    This function can be used by both sandbox callbacks and live callbacks.
    """

    try:
        # Create transaction entry
        transaction = MpesaTransaction(
            transaction_type=data.get('TransactionType'),
            trans_id=data.get('TransID'),
            trans_time=data.get('TransTime'),
            trans_amount=float(data.get('TransAmount', 0)),
            business_short_code=data.get('BusinessShortCode'),
            bill_ref_number=data.get('BillRefNumber'),
            msisdn=data.get('MSISDN'),
            first_name=data.get('FirstName', ''),
            middle_name=data.get('MiddleName', ''),
            last_name=data.get('LastName', ''),
            org_account_balance=data.get('OrgAccountBalance'),
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        logger.info(f"💾 Saved transaction {transaction.trans_id} for meter {transaction.bill_ref_number}")

        # Step 1️⃣: Update aggregates
        update_on_payment(
            db=db,
            meter_number=transaction.bill_ref_number,
            amount=transaction.trans_amount,
            msisdn=transaction.msisdn,
            trans_time=None
        )

        # Step 2️⃣: Trigger vending process
        vend_meter(
            db=db,
            meter_number=transaction.bill_ref_number,
            phone_number=transaction.msisdn,
            amount=transaction.trans_amount,
        )

        logger.info(f"✅ Transaction processed successfully for {transaction.bill_ref_number}")
        return transaction

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to process transaction: {str(e)}")
        raise
