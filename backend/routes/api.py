import json
import sqlite3
import urllib.parse
from http.server import BaseHTTPRequestHandler

from db import repository as repo
from db.database import connect


class Api(BaseHTTPRequestHandler):
    def reply(self, code, rows=None):
        body = b"" if rows is None else json.dumps([dict(r) for r in rows]).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urllib.parse.urlsplit(self.path)
        con = connect()
        if url.path == "/api/items":
            return self.reply(200, repo.list_items(con))
        if url.path == "/api/channels":
            return self.reply(200, repo.list_channels(con))
        if url.path == "/api/hits":
            return self.reply(200, repo.search_hits(con, dict(urllib.parse.parse_qsl(url.query))))
        self.reply(404)

    def do_POST(self):
        if self.path.startswith("/api/channels/"):
            with connect() as con:
                repo.toggle_channel(con, self.path.rsplit("/", 1)[-1])
            return self.reply(204)
        if self.path != "/api/items":
            return self.reply(404)
        try:
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            terms, max_price = body["terms"].strip(), body.get("max_price")
        except (ValueError, KeyError, TypeError, AttributeError):
            return self.reply(400)
        bad_price = max_price is not None and (type(max_price) not in (int, float) or max_price < 0)
        if not terms or len(terms) > 200 or bad_price:
            return self.reply(400)
        try:
            with connect() as con:
                repo.add_item(con, terms, max_price)
        except sqlite3.IntegrityError:
            return self.reply(409)
        self.reply(201)

    def do_DELETE(self):
        if not self.path.startswith("/api/items/"):
            return self.reply(404)
        with connect() as con:
            repo.delete_item(con, self.path.rsplit("/", 1)[-1])
        self.reply(204)
