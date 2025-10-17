from app.services.sms_services.base_sms import ISMSProvider
from app.utils.logger import get_logger

logger = get_logger("AfricasTalkingSMSService")

class AfricasTalkingSMSService(ISMSProvider):
    """Stub for Africa's Talking SMS Provider."""

    def __init__(self, username: str = None, api_key: str = None, sender_id: str = None):
        self.username = username or "AFRICASTALKING_USERNAME"
        self.api_key = api_key or "AFRICASTALKING_API_KEY"
        self.sender_id = sender_id or "SMARTWATER"

    def send_sms(self, phone_number: str, message: str):
        logger.info(
            f"🌍 [Africa's Talking Stub] Would send SMS to {phone_number}: {message}"
        )
        # In production:
        # import africastalking
        # africastalking.initialize(self.username, self.api_key)
        # sms = africastalking.SMS
        # sms.send(message, [phone_number], sender_id=self.sender_id)
        return {"status": "stubbed", "provider": "africastalking", "to": phone_number}
