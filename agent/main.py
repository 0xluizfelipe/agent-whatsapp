import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException

load_dotenv()

from agent.providers import get_provider
from agent.brain import Brain
from agent.memory import Memory

memory = Memory()
brain = Brain()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await memory.init_db()
    print("✅ Kotrac Agent — Catarina online")
    yield


app = FastAPI(title="Kotrac WhatsApp Agent", lifespan=lifespan)


@app.get("/")
async def root():
    return {"status": "online", "agent": "Catarina", "empresa": "Kotrac"}


@app.post("/reload")
async def reload_knowledge():
    """Recarrega a base de conhecimento da pasta knowledge/ sem reiniciar o servidor."""
    brain.reload_knowledge()
    return {"status": "ok", "message": "Base de conhecimento recarregada com sucesso."}


@app.get("/webhook")
async def verify_webhook(request: Request):
    provider = get_provider()
    return provider.verify_webhook(request)


@app.post("/webhook")
async def webhook(request: Request):
    provider = get_provider()
    try:
        message = await provider.parse_webhook(request)
        if not message:
            return {"status": "ok"}

        print(f"📩 [{message.phone}] {message.text}")

        history = await memory.get_history(message.phone)
        response_text = await brain.respond(message.text, history, message.phone)
        await memory.save_message(message.phone, message.text, response_text)
        await provider.send_message(message.phone, response_text)

        print(f"📤 [{message.phone}] {response_text[:80]}...")
        return {"status": "ok"}

    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))
