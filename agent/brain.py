import os
import yaml
import anthropic
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

# Extensões de arquivo suportadas na pasta knowledge/
SUPPORTED_EXTENSIONS = {".txt", ".md", ".yaml", ".yml", ".csv", ".json"}


class Brain:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-6"
        self.system_prompt = self._build_system_prompt()

    def _load_base_prompt(self) -> str:
        path = Path("config/prompts.yaml")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data["system_prompt"]

    def _load_knowledge(self) -> str:
        """Lê todos os arquivos da pasta knowledge/ e retorna como texto."""
        knowledge_dir = Path("knowledge")
        if not knowledge_dir.exists():
            return ""

        files = [f for f in knowledge_dir.iterdir()
                 if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS]

        if not files:
            return ""

        sections = []
        for file in sorted(files):
            try:
                content = file.read_text(encoding="utf-8").strip()
                if content:
                    sections.append(f"### {file.name}\n{content}")
            except Exception as e:
                print(f"[Brain] Erro ao ler {file.name}: {e}")

        if not sections:
            return ""

        return "\n\n## Base de Conhecimento\n" + "\n\n".join(sections)

    def _build_system_prompt(self) -> str:
        base = self._load_base_prompt()
        knowledge = self._load_knowledge()
        if knowledge:
            print(f"[Brain] Base de conhecimento carregada: {len(knowledge)} caracteres")
        return base + knowledge

    def reload_knowledge(self):
        """Recarrega a base de conhecimento sem reiniciar o servidor."""
        self.system_prompt = self._build_system_prompt()
        print("[Brain] Base de conhecimento recarregada.")

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
