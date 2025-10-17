# ============================================
# File: app/services/mpesa_service.py
# M-Pesa integration service with proper callback URLs
# ============================================

import requests
import base64
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_access_token():
    """
    Get M-Pesa OAuth access token
    Token expires in 3600 seconds (1 hour)
    """
    try:
        credentials = base64.b64encode(
            f"{settings.CONSUMER_KEY}:{settings.CONSUMER_SECRET}".encode()
        ).decode()

        headers = {"Authorization": f"Basic {credentials}"}
        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        
        logger.info("🔑 Requesting M-Pesa access token...")
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            token = response.json()["access_token"]
            logger.info(f"✅ Access token obtained: {token[:20]}...")
            return token
        else:
            error_msg = f"Failed to get token: {response.text}"
            logger.error(f"❌ {error_msg}")
            raise Exception(error_msg)
            
    except requests.exceptions.Timeout:
        logger.error("❌ M-Pesa API timeout")
        raise Exception("M-Pesa API timeout")
    except Exception as e:
        logger.error(f"❌ Token error: {str(e)}")
        raise


def register_urls(access_token: str):
    """
    Register callback URLs with Safaricom
    
    CRITICAL CHANGES:
    - Changed from /api/mpesa/... to /api/daraja/...
    - "daraja" is Swahili for "gateway" - no keyword issues!
    - These URLs will work with Safaricom's filters
    """
    try:
        url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # IMPORTANT: Using /api/daraja instead of /api/mpesa
        # "daraja" means "gateway" in Swahili - safe word!
        validation_url = f"{settings.NGROK_URL}/api/daraja/validation"
        confirmation_url = f"{settings.NGROK_URL}/api/daraja/confirmation"
        
        payload = {
            "ShortCode": settings.SHORTCODE,
            "ResponseType": "Completed",
            "ConfirmationURL": confirmation_url,
            "ValidationURL": validation_url
        }
        
        logger.info("📝 Registering C2B URLs...")
        logger.info(f"   Validation URL: {validation_url}")
        logger.info(f"   Confirmation URL: {confirmation_url}")
        logger.info("   ✅ No forbidden keywords ('mpesa', 'safaricom', etc.)")
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        result = response.json()
        
        if response.status_code == 200 and result.get('ResponseCode') == '0':
            logger.info(f"✅ URLs registered successfully: {result.get('ResponseDescription')}")
        else:
            logger.error(f"❌ URL registration failed: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ URL registration error: {str(e)}")
        raise


def simulate_payment(access_token: str, meter_number: str = "MTR001", amount: str = "100"):
    """
    Simulate C2B payment for testing
    
    Args:
        access_token: M-Pesa OAuth token
        meter_number: Meter number (used as BillRefNumber)
        amount: Payment amount in KSh
    """
    try:
        url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/simulate"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "ShortCode": settings.SHORTCODE,
            "CommandID": "CustomerPayBillOnline",
            "Amount": str(amount),
            "Msisdn": "254708374149",  # Sandbox test number
            "BillRefNumber": meter_number  # This is your meter number!
        }
        
        logger.info(f"💸 Simulating payment: {amount} KSh for meter {meter_number}")
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        result = response.json()
        
        if response.status_code == 200:
            logger.info(f"✅ Payment simulated: {result.get('ResponseDescription')}")
            if 'OriginatorCoversationID' in result:
                logger.info(f"📝 Originator Conversation ID: {result['OriginatorCoversationID']}")
        else:
            logger.error(f"❌ Payment simulation failed: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Payment simulation error: {str(e)}")
        raise


def query_transaction_status(access_token: str, transaction_id: str):
    """
    Query M-Pesa transaction status
    
    Args:
        access_token: M-Pesa OAuth token
        transaction_id: M-Pesa transaction ID (e.g., MBN31H462N)
    """
    try:
        url = "https://sandbox.safaricom.co.ke/mpesa/transactionstatus/v1/query"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Note: In production, you need to encrypt the security credential
        # For sandbox, you can use the test credential directly
        payload = {
            "Initiator": settings.INITIATOR_NAME,
            "SecurityCredential": settings.SECURITY_CREDENTIAL,
            "CommandID": "TransactionStatusQuery",
            "TransactionID": transaction_id,
            "PartyA": settings.SHORTCODE,
            "IdentifierType": "4",  # Organization shortcode
            "ResultURL": f"{settings.NGROK_URL}/api/mpesa/transaction-status/result",
            "QueueTimeOutURL": f"{settings.NGROK_URL}/api/mpesa/timeout",
            "Remarks": "Transaction status query",
            "Occasion": "Status check"
        }
        
        logger.info(f"🔍 Querying transaction status: {transaction_id}")
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        result = response.json()
        
        if response.status_code == 200:
            logger.info(f"✅ Status query submitted: {result.get('ResponseDescription')}")
        else:
            logger.error(f"❌ Status query failed: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Transaction status query error: {str(e)}")
        raise