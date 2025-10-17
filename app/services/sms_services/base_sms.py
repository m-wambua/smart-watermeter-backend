from abc import ABC, abstractmethod
from typing import List

class ISMSProvider(ABC):
    """Base interface for all SMS providers."""

    @abstractmethod
    def send_sms(self, to: str, message: str) -> bool:
        """Send a single SMS message."""
        pass

    @abstractmethod
    def send_bulk_sms(self, messages: List[dict]) -> bool:
        """Send multiple SMS messages (optional support)."""
        pass
