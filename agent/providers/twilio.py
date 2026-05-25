import os
import httpx
from fastapi import Request
from agent.providers.base import WhatsAppProvider, IncomingMessage


class TwilioProvider(WhatsAppProvider):
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")

    async def parse_webhook(self, request: Request) -> IncomingMessage | None:
        form = await request.form()
        body = form.get("Body", "").strip()
        from_number = str(form.get("From", "")).replace("whatsapp:", "")
        profile_name = str(form.get("ProfileName", ""))

        if not body or not from_number:
            return None

        return IncomingMessage(phone=from_number, text=body, name=profile_name)

    async def send_message(self, phone: str, text: str) -> None:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        to = f"whatsapp:{phone}" if not phone.startswith("whatsapp:") else phone
        from_wpp = (
            f"whatsapp:{self.from_number}"
            if not str(self.from_number).startswith("whatsapp:")
            else self.from_number
        )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data={"From": from_wpp, "To": to, "Body": text},
                auth=(self.account_sid, self.auth_token),
            )
            if response.status_code not in (200, 201):
                print(f"[Twilio] Erro ao enviar mensagem: {response.status_code} — {response.text}")
