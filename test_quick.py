import asyncio, os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.brain import Brain
from agent.memory import Memory

async def test():
    brain = Brain()
    memory = Memory()
    await memory.init_db()

    perguntas = [
        "Olá, o que vocês fazem?",
        "Tenho uma escavadeira com cilindro hidráulico vazando, vocês consertam?",
        "Qual o endereço de vocês?",
    ]

    phone = "+5521999999999"
    for p in perguntas:
        print(f"\nCliente: {p}")
        history = await memory.get_history(phone)
        resp = await brain.respond(p, history, phone)
        await memory.save_message(phone, p, resp)
        print(f"Catarina: {resp}")

asyncio.run(test())
