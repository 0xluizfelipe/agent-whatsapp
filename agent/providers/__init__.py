import os
from agent.providers.twilio import TwilioProvider


def get_provider():
    provider = os.getenv("WHATSAPP_PROVIDER", "twilio").lower()
    if provider == "twilio":
        return TwilioProvider()
    raise ValueError(f"Provedor desconhecido: {provider}. Use 'twilio'.")
