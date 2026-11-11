import asyncio
import threading
from http.server import ThreadingHTTPServer

from bot.telegram import run
from db.database import connect, init
from routes.api import Api

if __name__ == "__main__":
    with connect() as con:
        init(con)
    threading.Thread(target=ThreadingHTTPServer(("0.0.0.0", 8000), Api).serve_forever, daemon=True).start()
    asyncio.run(run())
