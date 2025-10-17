from app.services.sms_services.base_sms import ISMSProvider
from app.utils.logger import get_logger

logger = get_logger("TwilioSMSService")

class TwilioSMSService(ISMSProvider):
    """Stub for Twilio SMS Provider."""

    def __init__(self, account_sid: str = None, auth_token: str = None, from_number: str = None):
        self.account_sid = account_sid or "TWILIO_SID"
        self.auth_token = auth_token or "TWILIO_TOKEN"
        self.from_number = from_number or "+1234567890"

    def send_sms(self, phone_number: str, message: str):
        logger.info(
            f"📞 [Twilio Stub] Would send SMS to {phone_number}: {message}"
        )
        # In production:
        # client = Client(self.account_sid, self.auth_token)
        # client.messages.create(to=phone_number, from_=self.from_number, body=message)
        return {"status": "stubbed", "provider": "twilio", "to": phone_number}
