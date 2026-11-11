import re
import unicodedata

URL = re.compile(r"https?://\S+")
# ponytail: preço = menor "R$" da mensagem (ignora "R$ X OFF"); "frete R$ 20" ainda engana, refinar se incomodar
PRICE = re.compile(r"R\$\s*(?>(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d{2}))?)(?!\s*off)", re.I)


def norm(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


# ponytail: substring match ("tv" casa "atv"); troque por regex com \b se der falso positivo demais
def matches(terms, text):
    t = norm(text)
    return all(w in t for w in norm(terms).split())


def prices(text):
    return [int(i.replace(".", "")) + int(c or 0) / 100 for i, c in PRICE.findall(text)]


def dedup_key(text, price):
    """Mesma promo em canais diferentes: mesmo preço, ou mesmo texto sem os links."""
    return f"{price:.2f}" if price is not None else norm(URL.sub("", text)).strip()
