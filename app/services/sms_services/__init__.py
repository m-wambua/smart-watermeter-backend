import os
from app.services.sms_services.mock_sms import MockSMSProvider

from app.services.sms_services.twilio_sms import TwilioSMSService
from app.services.sms_services.africastalking import AfricasTalkingSMSService

def get_sms_service(provider: str = None):
    provider = provider or os.getenv("SMS_PROVIDER", "mock").lower()

    if provider == "twilio":
        return TwilioSMSService()
    elif provider == "africastalking":
        return AfricasTalkingSMSService()
    else:
        return MockSMSProvider()
