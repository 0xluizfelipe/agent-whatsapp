#!/usr/bin/env python3
"""Simulador de chat local — testa a Catarina sem precisar do WhatsApp."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from agent.brain import Brain
from agent.memory import Memory


async def chat():
    print("=" * 60)
    print("  Kotrac WhatsApp Agent — Simulador Local")
    print("  Agente: Catarina")
    print("  Digite 'sair' para encerrar")
    print("=" * 60)
    print()

    brain = Brain()
    memory = Memory()
    await memory.init_db()

    test_phone = "+5521999999999"

    while True:
        try:
            user_input = input("Você: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSimulador encerrado.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("sair", "exit", "quit"):
            print("Simulador encerrado.")
            break

        history = await memory.get_history(test_phone)
        response = await brain.respond(user_input, history, test_phone)
        await memory.save_message(test_phone, user_input, response)

        print(f"\nCatarina: {response}\n")


if __name__ == "__main__":
    asyncio.run(chat())
