# Rodar a partir de backend/:  python -m tests.test_alerts
from db import repository as repo
from db.database import connect, init
from services.alerts import process
from services.matcher import matches, prices

assert matches("rtx 4070", "🔥 Placa de vídeo RTX 4070 Super por R$ 3.499")
assert matches("pao de queijo", "Pão de Queijo congelado 1kg")  # ignora acento
assert not matches("rtx 4070", "RTX 4060 em promoção")  # exige todos os termos

assert prices("De R$ 4.000 por R$ 3.499,90 no pix") == [4000, 3499.9]
assert prices("R$1299 | cupom R$ 50 OFF") == [1299]
assert prices("R$ 50,00 off, R$ 3.499, no pix") == [3499]

con = connect(":memory:")
init(con)
repo.add_item(con, "rtx 4070", 3500)
repo.add_item(con, "cafeteira", None)


def p(chat, text, now=0):
    return process(con, chat, f"Canal {chat}", "https://t.me/x/1", text, now)


assert p(1, "RTX 4070 por R$ 3.499 https://a.co/1") == ["rtx 4070"]
assert p(2, "Oferta rtx 4070 só R$ 3.499,00 https://b.co/2") == []  # mesma promo, outro canal
assert p(2, "RTX 4070 R$ 3.799") == []  # acima do preço máximo
assert p(2, "RTX 4070 sem preço") == []  # preço máximo exige preço na mensagem
assert p(1, "RTX 4070 por R$ 3.499", now=13 * 3600) == ["rtx 4070"]  # janela de 12h passou
repo.toggle_channel(con, 1)
assert p(1, "Cafeteira R$ 199") == []  # canal desligado
assert p(2, "Cafeteira R$ 199") == ["cafeteira"]

assert len(repo.search_hits(con, {})) == 3
assert len(repo.search_hits(con, {"channel": "1"})) == 2
assert len(repo.search_hits(con, {"max": "500", "q": "cafeteira"})) == 1
assert len(repo.search_hits(con, {"from": "1", "item": "rtx 4070"})) == 1
assert [h["terms"] for h in repo.search_hits(con, {"after": "2"})] == ["cafeteira"]
print("ok")
