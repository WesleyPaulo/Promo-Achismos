import asyncio
import os
import re
import time

from telethon import Button, TelegramClient, events

from db import repository as repo
from db.database import DB_PATH, connect
from services.alerts import process

PROMPT = "Toque para ligar/desligar um canal:"


def channel_buttons():
    # ponytail: Telegram aceita ~100 botões por mensagem; paginar se seguir mais canais que isso
    return [[Button.inline(("✅ " if c["enabled"] else "⛔ ") + c["title"][:40], f"ch:{c['id']}".encode())]
            for c in repo.list_channels(connect(), limit=100)]


async def run():
    data = os.path.dirname(DB_PATH)
    api_id, api_hash = int(os.environ["API_ID"]), os.environ["API_HASH"]
    client = TelegramClient(os.path.join(data, "session"), api_id, api_hash)  # sua conta: lê os canais
    bot = TelegramClient(os.path.join(data, "bot"), api_id, api_hash)  # bot: avisos e botões
    await client.start(phone=lambda: input("Telefone da SUA conta, com DDI (ex: +5511999999999): "))
    await bot.start(bot_token=os.environ["BOT_TOKEN"])
    me = (await client.get_me()).id

    async def sync_channels():
        with connect() as con:
            async for d in client.iter_dialogs():
                if d.is_channel and not d.is_group:
                    repo.upsert_channel(con, d.id, d.name)

    @client.on(events.NewMessage(func=lambda e: e.is_channel and not e.is_group))
    async def on_channel_message(event):
        chat = await event.get_chat()
        link = f"https://t.me/{chat.username}/{event.id}" if chat.username else f"https://t.me/c/{chat.id}/{event.id}"
        text = event.raw_text or ""
        with connect() as con:
            hits = process(con, event.chat_id, chat.title, link, text, int(time.time()))
        if hits:
            await bot.send_message(me, f"🔔 {', '.join(hits)} — {chat.title}\n{link}\n\n{text[:800]}", link_preview=False)

    @bot.on(events.NewMessage(pattern="/canais", from_users=me))
    async def on_canais(event):
        await sync_channels()
        await event.respond(PROMPT, buttons=channel_buttons() or None)

    @bot.on(events.CallbackQuery(data=re.compile(rb"ch:")))
    async def on_toggle(event):
        if event.sender_id != me:
            return await event.answer("Sem permissão")
        with connect() as con:
            repo.toggle_channel(con, int(event.data[3:]))
        await event.edit(PROMPT, buttons=channel_buttons())
        await event.answer("Atualizado")

    await sync_channels()
    print("Escutando canais. UI em http://localhost:8000 — mande /canais pro bot.", flush=True)
    await asyncio.gather(client.run_until_disconnected(), bot.run_until_disconnected())
