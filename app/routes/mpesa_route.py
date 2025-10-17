# ============================================
# File: app/routes/mpesa_routes.py
# CORRECTED: Callbacks that work for both M-Pesa (POST) and browser testing (GET)
# ============================================

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.payment import MpesaTransaction
from app.services.mpesa_services import get_access_token, register_urls, simulate_payment
from app.utils.logger import get_logger
import json
from typing import Optional
from app.core.config import settings
from app.services.vending_services import vend_meter
# IMPORTANT: DO NOT use "mpesa" in the prefix!
# Use a different word that doesn't trigger Safaricom's keyword filter
mpesa_router = APIRouter(prefix="/api/daraja", tags=["Daraja"])  # Changed from /api/mpesa
logger = get_logger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================
# CALLBACK ENDPOINTS
# Now support BOTH GET (testing) and POST (M-Pesa)
# ============================================

@mpesa_router.api_route("/validation", methods=["GET", "POST"])
async def c2b_validation(request: Request, db: Session = Depends(get_db)):
    """
    M-Pesa Validation Callback
    Accepts both GET (for testing) and POST (from M-Pesa)
    """
    try:
        # Check if it's a GET request (testing)
        if request.method == "GET":
            logger.info("🧪 GET request to validation endpoint (testing)")
            return {
                "status": "validation endpoint is working",
                "method": "GET",
                "note": "M-Pesa will POST to this endpoint"
            }
        
        # POST request - actual M-Pesa callback
        data = await request.json()
        logger.info(f"🔥 Validation Callback Received (POST)")
        logger.info(f"Data: {json.dumps(data, indent=2)}")
        
        # Extract data
        bill_ref_number = data.get('BillRefNumber', '')
        trans_amount = data.get('TransAmount', 0)
        msisdn = data.get('MSISDN', '')
        
        # Validate meter number
        if not bill_ref_number:
            logger.warning("❌ Missing BillRefNumber")
            return {"ResultCode": "C2B00011", "ResultDesc": "Invalid account number"}
        
        # Validate amount
        if trans_amount < 1:
            logger.warning(f"❌ Amount too low: {trans_amount}")
            return {"ResultCode": "C2B00013", "ResultDesc": "Amount too low"}
        
        logger.info(f"✅ Validation passed for meter: {bill_ref_number}, amount: {trans_amount}")
        return {"ResultCode": 0, "ResultDesc": "Accepted"}
        
    except Exception as e:
        logger.error(f"❌ Validation error: {str(e)}")
        return {"ResultCode": 0, "ResultDesc": "Accepted"}


@mpesa_router.api_route("/confirmation", methods=["GET", "POST"])
async def c2b_confirmation(request: Request, db: Session = Depends(get_db)):
    """
    M-Pesa Confirmation Callback
    Accepts both GET (for testing) and POST (from M-Pesa)
    """
    try:
        # Check if it's a GET request (testing)
        if request.method == "GET":
            logger.info("🧪 GET request to confirmation endpoint (testing)")
            
            # Count transactions
            txn_count = db.query(MpesaTransaction).count()
            
            return {
                "status": "confirmation endpoint is working",
                "method": "GET",
                "note": "M-Pesa will POST to this endpoint",
                "transactions_received": txn_count
            }
        
        # POST request - actual M-Pesa callback
        data = await request.json()
        logger.info(f"✅ Confirmation Callback Received (POST)")
        logger.info(f"Data: {json.dumps(data, indent=2)}")
        
        # Save transaction
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
        
        logger.info(f"💾 Transaction saved: ID={transaction.id}, TransID={transaction.trans_id}")
        
        return {"ResultCode": 0, "ResultDesc": "Success"}
        
    except Exception as e:
        logger.error(f"❌ Confirmation error: {str(e)}")
        db.rollback()
        return {"ResultCode": 0, "ResultDesc": "Accepted"}


@mpesa_router.api_route("/timeout", methods=["GET", "POST"])
async def mpesa_timeout(request: Request):
    """
    M-Pesa Timeout Callback
    """
    if request.method == "GET":
        return {
            "status": "timeout endpoint is working",
            "method": "GET"
        }
    
    try:
        data = await request.json()
        logger.warning(f"⏰ Timeout Callback: {json.dumps(data, indent=2)}")
        return {"ResultCode": 0, "ResultDesc": "Timeout received"}
    except Exception as e:
        logger.error(f"Timeout error: {str(e)}")
        return {"ResultCode": 0, "ResultDesc": "Accepted"}


# ============================================
# ADMIN ENDPOINTS
# ============================================

@mpesa_router.get("/register-urls")
async def register_urls_endpoint():
    """
    Register callback URLs with Safaricom
    IMPORTANT: Run this after starting ngrok
    """
    try:
        logger.info("📝 Registering C2B URLs...")
        token = get_access_token()
        result = register_urls(token)
        
        logger.info(f"✅ URLs registered")
        logger.info(f"Response: {json.dumps(result, indent=2)}")
        
        return {
            "success": True,
            "message": "URLs registered successfully",
            "data": result,
            "urls": {
                "validation": f"{settings.NGROK_URL}/api/daraja/validation",
                "confirmation": f"{settings.NGROK_URL}/api/daraja/confirmation"
            }
        }
    except Exception as e:
        logger.error(f"❌ URL registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@mpesa_router.get("/simulate-payment")
async def simulate_payment_endpoint(
    meter_number: Optional[str] = "MTR001",
    amount: Optional[str] = "100",
    db: Session = Depends(get_db)
):
    """
    Simulate C2B payment using Daraja sandbox,
    then trigger vending + SMS locally when successful.
    """
    try:
        logger.info(f"💸 Initiating sandbox simulation: {amount} KSh for meter {meter_number}")

        # STEP 1: Call Daraja sandbox to simulate a payment
        token = get_access_token()
        result = simulate_payment(token, meter_number, amount)
        logger.info(f"✅ Sandbox response: {json.dumps(result, indent=2)}")

        # STEP 2: Verify success from Safaricom sandbox
        if result.get("ResponseDescription") != "Accept the service request successfully.":
            logger.warning(f"❌ Sandbox rejected simulation: {result}")
            return {
                "success": False,
                "message": "Sandbox rejected payment simulation",
                "daraja_result": result
            }

        # STEP 3: Store a local transaction (simulating callback)
        simulated_trans_id = result.get("OriginatorConversationID", "SIM-" + str(amount))
        transaction = MpesaTransaction(
            transaction_type="Pay Bill",
            trans_id=simulated_trans_id,
            trans_time="20251016120000",  # mock time
            trans_amount=float(amount),
            business_short_code=settings.SHORTCODE,
            bill_ref_number=meter_number,
            msisdn="254708374149",  # Safaricom sandbox test number
            first_name="Test",
            middle_name="",
            last_name="User",
            org_account_balance="0.00",
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        logger.info(f"💾 Simulated transaction stored: {transaction.trans_id}")

        # STEP 4: Trigger vending + SMS
        logger.info(f"⚙️ Triggering vending for meter {meter_number}")
        vended_token = vend_meter(db, meter_number, transaction.msisdn, float(amount))
        logger.info(f"✅ Vending completed for meter {meter_number} → token: {vended_token.token}")

        # STEP 5: Return consolidated result
        return {
            "success": True,
            "message": "Full payment simulation and vending completed",
            "daraja_result": result,
            "transaction": {
                "trans_id": transaction.trans_id,
                "amount": transaction.trans_amount,
                "msisdn": transaction.msisdn,
                "meter_number": transaction.bill_ref_number
            },
            "vending_result": {
                "token": vended_token.token,
                "units": vended_token.units,
                "timestamp": str(vended_token.timestamp)
            }
        }

    except Exception as e:
        logger.error(f"❌ Simulation pipeline failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@mpesa_router.get("/test-connection")
async def test_mpesa_connection():
    """Test M-Pesa API connectivity"""
    try:
        logger.info("🔌 Testing M-Pesa connection...")
        token = get_access_token()
        return {
            "success": True,
            "message": "M-Pesa connection successful",
            "token_length": len(token),
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        logger.error(f"❌ Connection test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@mpesa_router.get("/transactions")
async def get_transactions(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get recent transactions"""
    transactions = db.query(MpesaTransaction).order_by(
        MpesaTransaction.id.desc()
    ).limit(limit).all()
    
    return {
        "success": True,
        "count": len(transactions),
        "transactions": [
            {
                "id": txn.id,
                "trans_id": txn.trans_id,
                "trans_amount": txn.trans_amount,
                "bill_ref_number": txn.bill_ref_number,
                "msisdn": txn.msisdn,
                "trans_time": txn.trans_time,
                "first_name": txn.first_name,
                "last_name": txn.last_name
            }
            for txn in transactions
        ]
    }


@mpesa_router.get("/transactions/{trans_id}")
async def get_transaction(
    trans_id: str,
    db: Session = Depends(get_db)
):
    """Get specific transaction"""
    transaction = db.query(MpesaTransaction).filter(
        MpesaTransaction.trans_id == trans_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return {
        "success": True,
        "transaction": {
            "id": transaction.id,
            "trans_id": transaction.trans_id,
            "trans_amount": transaction.trans_amount,
            "bill_ref_number": transaction.bill_ref_number,
            "msisdn": transaction.msisdn,
            "trans_time": transaction.trans_time,
            "first_name": transaction.first_name,
            "middle_name": transaction.middle_name,
            "last_name": transaction.last_name,
            "business_short_code": transaction.business_short_code,
            "org_account_balance": transaction.org_account_balance
        }
    }


# ============================================
# DEBUGGING ENDPOINT
# ============================================

@mpesa_router.get("/debug/routes")
async def debug_routes():
    """Show all registered routes for this router"""
    routes = []
    for route in mpesa_router.routes:
        routes.append({
            "path": route.path,
            "name": route.name,
            "methods": route.methods
        })
    
    return {
        "router_prefix": "/api/daraja",
        "routes": routes,
        "callback_urls": {
            "validation": f"{settings.NGROK_URL}/api/daraja/validation",
            "confirmation": f"{settings.NGROK_URL}/api/daraja/confirmation",
            "timeout": f"{settings.NGROK_URL}/api/daraja/timeout"
        }
    }
    
router = APIRouter(prefix="/api/mpesa", tags=["M-Pesa"])
logger = get_logger("M-Pesa")    
@router.post("/callback")
def mpesa_callback(payload: dict, db: Session = Depends(get_db)):
    logger.info("📥 Received simulated M-Pesa callback")
    logger.info(payload)

    # Save payment record
    payment = MpesaTransaction(
        trans_id=payload.get("TransID"),
        trans_amount=float(payload.get("TransAmount")),
        msisdn=payload.get("MSISDN"),
        first_name=payload.get("FirstName"),
        last_name=payload.get("LastName"),
        bill_ref_number=payload.get("BillRefNumber"),
        business_short_code="123456",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    # Trigger vending immediately
    vend_meter(
        db=db,
        meter_number=payment.bill_ref_number,
        phone_number=payment.msisdn,
        amount=payment.trans_amount,
    )

    return {"ResultCode": 0, "ResultDesc": "Accepted"}