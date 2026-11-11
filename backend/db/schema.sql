CREATE TABLE IF NOT EXISTS items (
  id INTEGER PRIMARY KEY,
  terms TEXT NOT NULL UNIQUE,
  max_price REAL
);

CREATE TABLE IF NOT EXISTS channels (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  enabled INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS hits (
  id INTEGER PRIMARY KEY,
  ts INTEGER NOT NULL,
  item_id INTEGER,
  terms TEXT NOT NULL,
  channel_id INTEGER,
  channel TEXT,
  price REAL,
  link TEXT,
  text TEXT,
  dedup_key TEXT
);

CREATE INDEX IF NOT EXISTS hits_dedup ON hits (item_id, dedup_key, ts);
