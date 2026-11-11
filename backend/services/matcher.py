import re
import unicodedata

URL = re.compile(r"https?://\S+")
# Preço = menor "R$" da mensagem que não seja parcela, cupom, frete etc. ("R$ X OFF" também é ignorado).
PRICE = re.compile(r"R\$\s*(?>(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d{2}))?)(?!\s*off)", re.I)
# Texto logo antes do "R$" que indica que o valor não é o preço do produto:
# "12x R$ 198", "12x sem juros de R$", "parcelas de R$", "cupom de R$100", "frete: R$ 20", "economize R$ 500"
NOT_PRICE = re.compile(r"(\d+\s*x(\s*sem\s*juros)?|parcelas?|cupom|frete|cashback|desconto|economi\w*)\s*(de|:)?\s*$", re.I)
NOT_PRICE_WINDOW = 25  # caracteres olhados antes do "R$"


def norm(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


# ponytail: substring match ("tv" casa "atv"); troque por regex com \b se der falso positivo demais
def matches(terms, text):
    t = norm(text)
    return all(w in t for w in norm(terms).split())


def prices(text):
    return [int(m[1].replace(".", "")) + int(m[2] or 0) / 100
            for m in PRICE.finditer(text)
            if not NOT_PRICE.search(text[max(0, m.start() - NOT_PRICE_WINDOW):m.start()])]


def dedup_key(text, price):
    """Mesma promo em canais diferentes: mesmo preço, ou mesmo texto sem os links."""
    return f"{price:.2f}" if price is not None else norm(URL.sub("", text)).strip()
