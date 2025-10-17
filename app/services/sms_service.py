from app.services.sms_services.provider_factory import get_sms_provider
from app.utils.logger import get_logger

logger = get_logger(__name__)

class SMSService:
    """Central SMS service used across the backend."""

    def __init__(self, provider_name: str = "mock"):
        self.provider = get_sms_provider(provider_name)

    def send_token_sms(self, phone_number: str, token: str, units: float, meter: str):
        message = (
            f"SmartWater Vending\n"
            f"Meter: {meter}\n"
            f"Units: {units}\n"
            f"Token: {token}\n"
            f"Thank you for using SmartWater!"
        )
        success = self.provider.send_sms(phone_number, message)
        if success:
            logger.info(f"✅ SMS sent successfully to {phone_number}")
        else:
            logger.error(f"❌ Failed to send SMS to {phone_number}")
        return success
