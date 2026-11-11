from db import repository as repo
from services.matcher import dedup_key, matches, prices

# ponytail: dois produtos diferentes do mesmo item com preço idêntico na janela viram um aviso só
DEDUP_SECONDS = 12 * 3600


def best_price(text):
    return min(prices(text), default=None)


def price_ok(item, price):
    """Item sem preço máximo sempre passa; com máximo, exige preço na mensagem e ≤ máximo."""
    return item["max_price"] is None or (price is not None and price <= item["max_price"])


def process(con, chat_id, title, link, text, now):
    """Grava os avisos novos de uma mensagem de canal e devolve os termos que dispararam."""
    if not repo.ensure_channel(con, chat_id, title):
        return []
    price = best_price(text)
    key = dedup_key(text, price)
    hits = []
    for item in repo.list_items(con):
        if not matches(item["terms"], text) or not price_ok(item, price):
            continue
        if repo.recent_hit_exists(con, item["id"], key, now - DEDUP_SECONDS):
            continue
        repo.add_hit(con, now, item, chat_id, title, price, link, text, key)
        hits.append(item["terms"])
    return hits
