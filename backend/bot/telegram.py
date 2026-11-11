import asyncio
import os
import re
import time

from telethon import Button, TelegramClient, events

from db import repository as repo
from db.database import DB_PATH, connect
from services.alerts import best_price, price_ok, process
from services.matcher import matches

PROMPT = "Toque para ligar/desligar um canal:"
HELP = ("Promo Achismos ativo.\n\n"
        "/canais  ligar/desligar canais\n"
        "/testar  roda as regras nas últimas 50 mensagens de cada canal ligado (sem avisar nem gravar)")
STATUS_SECONDS = 300
SCAN_LIMIT = 50


def channel_buttons():
    # ponytail: Telegram aceita ~100 botões por mensagem; paginar se seguir mais canais que isso
    return [[Button.inline(("✅ " if c["enabled"] else "⛔ ") + c["title"][:40], f"ch:{c['id']}".encode())]
            for c in repo.list_channels(connect(), limit=100)]


def message_link(chat, msg_id):
    username = getattr(chat, "username", None)
    return f"https://t.me/{username}/{msg_id}" if username else f"https://t.me/c/{chat.id}/{msg_id}"


def ago(ts):
    m = int(time.time() - ts) // 60
    return f"{m} min" if m < 120 else f"{m // 60} h"


def fmt_price(p):
    return "sem preço" if p is None else "R$ " + f"{p:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


async def run():
    data = os.path.dirname(DB_PATH)
    api_id, api_hash = int(os.environ["API_ID"]), os.environ["API_HASH"]
    client = TelegramClient(os.path.join(data, "session"), api_id, api_hash)  # sua conta: lê os canais
    bot = TelegramClient(os.path.join(data, "bot"), api_id, api_hash)  # bot: avisos e botões
    await client.start(phone=lambda: input("Telefone da SUA conta, com DDI (ex: +5511999999999): "))
    await bot.start(bot_token=os.environ["BOT_TOKEN"])
    me = (await client.get_me()).id
    stats = {"msgs": 0, "hits": 0, "live": 0, "raw": 0}
    started = time.time()

    async def sync_channels():
        with connect() as con:
            async for d in client.iter_dialogs():
                if d.is_channel and not d.is_group:
                    repo.upsert_channel(con, d.id, d.name)

    async def status_log():
        while True:
            await asyncio.sleep(STATUS_SECONDS)
            print(f"[status] últimos {STATUS_SECONDS // 60} min: {stats['msgs']} mensagens de canais, "
                  f"{stats['hits']} avisos, {stats['raw']} updates do Telegram (conexão viva se > 0)", flush=True)
            stats.update(msgs=0, hits=0, raw=0)

    @client.on(events.Raw)
    async def on_raw(_):
        stats["raw"] += 1

    @client.on(events.NewMessage(func=lambda e: e.is_channel and not e.is_group))
    async def on_channel_message(event):
        stats["msgs"] += 1
        stats["live"] += 1
        chat = await event.get_chat()
        link = message_link(chat, event.id)
        text = event.raw_text or ""
        with connect() as con:
            hits = process(con, event.chat_id, chat.title, link, text, int(time.time()))
        if hits:
            stats["hits"] += len(hits)
            print(f"[aviso] {', '.join(hits)} — {chat.title} — {link}", flush=True)
            await bot.send_message(me, f"🔔 {', '.join(hits)} — {chat.title}\n{link}\n\n{text[:800]}", link_preview=False)

    @bot.on(events.NewMessage(pattern="/start", from_users=me))
    async def on_start(event):
        await event.respond(HELP)

    @bot.on(events.NewMessage(pattern="/canais", from_users=me))
    async def on_canais(event):
        await sync_channels()
        await event.respond(PROMPT, buttons=channel_buttons() or None)

    @bot.on(events.NewMessage(pattern="/testar", from_users=me))
    async def on_testar(event):
        con = connect()
        items = repo.list_items(con)
        channels = [c for c in repo.list_channels(con) if c["enabled"]]
        await event.respond(f"Lendo as últimas {SCAN_LIMIT} mensagens de {len(channels)} canais ligados...")
        total, found, newest = 0, [], None
        for c in channels:
            async for m in client.iter_messages(c["id"], limit=SCAN_LIMIT):
                total += 1
                if newest is None or m.date > newest[0]:
                    newest = (m.date, c["title"])
                text = m.raw_text or ""
                price = best_price(text)
                for it in items:
                    if matches(it["terms"], text):
                        found.append((price_ok(it, price), it["terms"], price, c["title"], message_link(await m.get_chat(), m.id)))
        ok = sum(f[0] for f in found)
        lines = [f"{'[OK]' if f[0] else '[preço]'} {f[1]} · {fmt_price(f[2])} · {f[3]}\n{f[4]}" for f in found[:15]]
        await event.respond(
            f"Monitor ao vivo: {stats['live']} mensagens recebidas desde que iniciou (há {ago(started)})\n"
            + (f"Mais recente nos canais: há {ago(newest[0].timestamp())} em {newest[1]}\n\n" if newest else "\n")
            + f"Mensagens lidas: {total}\nItens encontrados no texto: {len(found)}\nPassariam no preço máximo: {ok}"
            + ("\n\n" + "\n\n".join(lines) if lines else "\n\nNenhuma das mensagens recentes cita seus itens."),
            link_preview=False)

    @bot.on(events.CallbackQuery(data=re.compile(rb"ch:")))
    async def on_toggle(event):
        if event.sender_id != me:
            return await event.answer("Sem permissão")
        with connect() as con:
            repo.toggle_channel(con, int(event.data[3:]))
        await event.edit(PROMPT, buttons=channel_buttons())
        await event.answer("Atualizado")

    await sync_channels()
    print("Escutando canais. UI em http://localhost:8000 — mande /canais ou /testar pro bot.", flush=True)
    await asyncio.gather(client.run_until_disconnected(), bot.run_until_disconnected(), status_log())
