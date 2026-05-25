from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from fastapi import Request


@dataclass
class IncomingMessage:
    phone: str
    text: str
    name: str = field(default="")


class WhatsAppProvider(ABC):
    @abstractmethod
    async def parse_webhook(self, request: Request) -> IncomingMessage | None:
        pass

    @abstractmethod
    async def send_message(self, phone: str, text: str) -> None:
        pass

    def verify_webhook(self, request: Request):
        return {"status": "ok"}
