from app.services.sms_services.base_sms import ISMSProvider
from app.utils.logger import get_logger

logger = get_logger(__name__)

class MockSMSProvider(ISMSProvider):
    """Mock SMS service for development."""

    def send_sms(self, to: str, message: str) -> bool:
        logger.info(f"📱 Mock SMS → {to}: {message}")
        return True

    def send_bulk_sms(self, messages):
        for msg in messages:
            logger.info(f"📱 Mock BULK SMS → {msg['to']}: {msg['message']}")
        return True
