# Todas as queries SQL do projeto.


def list_items(con):
    return con.execute("SELECT * FROM items ORDER BY id DESC").fetchall()


def add_item(con, terms, max_price):
    con.execute("INSERT INTO items (terms, max_price) VALUES (?, ?)", (terms, max_price))


def delete_item(con, item_id):
    con.execute("DELETE FROM items WHERE id = ?", (item_id,))


def list_channels(con, limit=-1):
    return con.execute("SELECT * FROM channels ORDER BY title COLLATE NOCASE LIMIT ?", (limit,)).fetchall()


def upsert_channel(con, chat_id, title):
    con.execute("INSERT INTO channels (id, title) VALUES (?, ?)"
                " ON CONFLICT(id) DO UPDATE SET title = excluded.title", (chat_id, title))


def ensure_channel(con, chat_id, title):
    """Cadastra o canal se for novo (ligado) e diz se está ligado."""
    con.execute("INSERT OR IGNORE INTO channels (id, title) VALUES (?, ?)", (chat_id, title))
    return bool(con.execute("SELECT enabled FROM channels WHERE id = ?", (chat_id,)).fetchone()["enabled"])


def toggle_channel(con, chat_id):
    con.execute("UPDATE channels SET enabled = 1 - enabled WHERE id = ?", (chat_id,))


def recent_hit_exists(con, item_id, dedup_key, since):
    return con.execute("SELECT 1 FROM hits WHERE item_id = ? AND dedup_key = ? AND ts > ?",
                       (item_id, dedup_key, since)).fetchone() is not None


def add_hit(con, ts, item, chat_id, channel, price, link, text, dedup_key):
    con.execute("INSERT INTO hits (ts, item_id, terms, channel_id, channel, price, link, text, dedup_key)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (ts, item["id"], item["terms"], chat_id, channel, price, link, text, dedup_key))


HIT_FILTERS = {  # parâmetro da URL -> trecho SQL fixo (valores sempre via ?)
    "q": "text LIKE '%' || ? || '%'",
    "item": "terms = ?",
    "channel": "channel_id = ?",
    "min": "price >= ?",
    "max": "price <= ?",
    "from": "ts >= ?",
    "to": "ts <= ?",
    "after": "id > ?",  # só avisos novos (usado pelas notificações do site)
}


def search_hits(con, params, limit=500):
    used = [k for k in HIT_FILTERS if params.get(k)]
    where = " AND ".join(HIT_FILTERS[k] for k in used) or "1"
    return con.execute(f"SELECT * FROM hits WHERE {where} ORDER BY ts DESC LIMIT ?",
                       [params[k] for k in used] + [limit]).fetchall()
