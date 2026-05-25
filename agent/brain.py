import os
import yaml
import anthropic
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)


class Brain:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-6"
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        path = Path("config/prompts.yaml")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data["system_prompt"]

    async def respond(self, message: str, history: list[dict], phone: str) -> str:
        messages = []
        for h in history[-10:]:
            messages.append({"role": "user", "content": h["user"]})
            messages.append({"role": "assistant", "content": h["assistant"]})
        messages.append({"role": "user", "content": message})

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=self.system_prompt,
            messages=messages,
        )
        return response.content[0].text
