from app.services.sms_services.mock_sms import MockSMSProvider
# Future imports can go here: from app.services.sms_services.twilio_sms import TwilioSMSProvider, etc.

def get_sms_provider(provider_name: str = "mock"):
    """Returns an instance of the requested SMS provider."""
    if provider_name == "mock":
        return MockSMSProvider()
    # elif provider_name == "twilio":
    #     return TwilioSMSProvider()
    # elif provider_name == "africas_talking":
    #     return AfricasTalkingProvider()
    else:
        raise ValueError(f"Unknown SMS provider: {provider_name}")
