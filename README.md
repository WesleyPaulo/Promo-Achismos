# Promo Achismos

> Monitor de promoções no Telegram: cadastre os produtos que você quer e receba um aviso no seu bot assim que eles aparecerem nos canais de ofertas que você segue, com preço máximo por item, sem avisos repetidos, escolha de canais e histórico com filtros. Python + Telethon + SQLite, Vue 3 + Tailwind, Docker.

---

## Sumário

- [O que ele faz](#o-que-ele-faz)
- [Como funciona](#como-funciona)
- [Requisitos](#requisitos)
- [Instalação passo a passo](#instalação-passo-a-passo)
- [Uso](#uso)
- [Regras de detecção](#regras-de-detecção)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [API HTTP](#api-http)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Desenvolvimento](#desenvolvimento)
- [Operação: logs, backup, atualização](#operação-logs-backup-atualização)
- [Solução de problemas](#solução-de-problemas)
- [Segurança](#segurança)
- [Limitações conhecidas](#limitações-conhecidas)
- [Licença](#licença)

---

## O que ele faz

- **Cadastro de itens de interesse**: termos como `rtx 4070` ou `air fryer`, com **preço máximo** opcional.
- **Monitoramento automático** de todos os canais que a sua conta do Telegram segue.
- **Aviso no Telegram** por um bot seu: termo encontrado, canal, link direto para a mensagem e o texto da oferta.
- **Sem repetição**: a mesma promoção postada em vários canais gera um aviso só.
- **Escolha de canais**: ligue/desligue canais na página ou no bot com `/canais` (botões interativos).
- **Histórico de avisos** com filtros por texto, item, canal, faixa de preço e período.

## Como funciona

```
 Canais de promoção ──► Sua conta (Telethon) ──► backend ──► SQLite
                                                   │  ▲
                              aviso + /canais ◄────┘  │ /api
                                   (bot)              │
                               Navegador ──► nginx (frontend Vue)
```

- O **backend** entra no Telegram com **duas sessões**:
  - **Sua conta**: lê as mensagens dos canais. Precisa ser a sua conta porque um bot só lê canais em que ele é administrador.
  - **Seu bot**: envia os avisos e responde a `/canais`.
- Cada mensagem nova de canal é comparada com os itens cadastrados. Se bater (e passar no preço máximo e na checagem de duplicados), o aviso vai para o seu chat com o bot e é gravado no histórico.
- O **frontend** é servido por um nginx, que repassa `/api` para o backend.

## Requisitos

- [Docker](https://docs.docker.com/get-docker/) com Docker Compose v2
- Uma conta do Telegram
- Para desenvolvimento sem Docker: Python 3.11+ e Node.js 20+

## Instalação passo a passo

### 1. Credenciais da API do Telegram (`API_ID` e `API_HASH`)

1. Acesse <https://my.telegram.org> e entre com o seu número.
2. Abra **API development tools**.
3. Preencha **App title** e **Short name** (sem a palavra "Telegram"). URL e descrição são opcionais, e qualquer plataforma serve.
4. Clique em **Create application** e copie o **api_id** e o **api_hash**.

> Se aparecer só "ERROR", desative bloqueadores (Brave Shields, adblock) ou a VPN e tente de novo.

### 2. Criar o bot (`BOT_TOKEN`)

1. No Telegram, abra o [@BotFather](https://t.me/BotFather) e envie `/newbot`.
2. Escolha um nome e um usuário terminado em `bot`.
3. Copie o token que ele devolver.
4. **Abra o seu bot e envie `/start`.** Sem isso o bot não consegue mandar mensagens para você.

### 3. Configurar o `.env`

```sh
cp .env.example .env
```

Preencha os três valores (veja [Variáveis de ambiente](#variáveis-de-ambiente)).

### 4. Primeiro login (só uma vez)

```sh
docker compose run --rm backend
```

O terminal pede:

1. **o telefone da sua conta** com DDI (ex.: `+5511999999999`), e não o token do bot;
2. o **código** que o Telegram envia no app;
3. a **senha de verificação em duas etapas**, se você tiver.

Quando aparecer `Escutando canais...`, o login está salvo em `./data`. Pare com `Ctrl+C`.

### 5. Subir

```sh
docker compose up -d --build
```

Abra <http://localhost:8000>.

## Uso

### Página web (`http://localhost:8000`)

| Aba | O que faz |
|---|---|
| **01 Itens** | Cadastra termos e o preço máximo opcional, e remove itens. |
| **02 Canais** | Lista os canais que você segue; clique para ligar/desligar (ON/OFF). Canais novos entram ligados. |
| **03 Histórico** | Avisos enviados, com filtros por texto, item, canal, preço mín./máx. e período. Atualiza a cada 30 s e mostra os 500 mais recentes. |

A página se atualiza sozinha a cada 30 s: itens, canais (inclusive mudanças feitas pelo `/canais` no bot), histórico e o indicador **API ONLINE/OFFLINE**, que mostra se a página está conseguindo falar com o backend.

**Notificações no navegador**: clique em **NOTIF** no topo e permita quando o navegador pedir. A cada ocorrência nova aparece uma notificação do sistema (item, preço, canal); clicar abre a mensagem no Telegram. Detalhes:

- Funciona com o site **aberto em alguma aba**, mesmo em segundo plano ou minimizado. Com o site fechado, quem avisa é o bot do Telegram.
- Exige `http://localhost` ou HTTPS. Pelo IP da rede (`http://192.168...`) o navegador não permite notificações.
- Em abas em segundo plano o navegador pode espaçar as checagens para cerca de 1 por minuto.
- Se aparecer **NOTIF BLOQUEADAS**, libere em *Permissões do site*, no ícone ao lado do endereço.

### Bot do Telegram

| Comando | O que faz |
|---|---|
| `/start` | Libera o bot para te mandar mensagens (obrigatório uma vez) e mostra os comandos. |
| `/canais` | Atualiza a lista de canais e mostra botões para ligar/desligar cada um. |
| `/testar` | Diagnóstico: roda as regras nas últimas 50 mensagens de cada canal ligado (sem avisar nem gravar) e compara a mensagem mais recente dos canais com o que o monitor recebeu ao vivo. |

Só a sua conta pode usar os botões; outras pessoas recebem "Sem permissão".

Exemplo de aviso:

```
🔔 rtx 4070 — Hardware BR
https://t.me/hardwarebr/12345

Placa de vídeo RTX 4070 Super 12GB por R$ 3.499 no pix
```

## Regras de detecção

| Regra | Como funciona |
|---|---|
| **Match** | Todas as palavras do item precisam aparecer na mensagem, em qualquer ordem, sem diferenciar maiúsculas/minúsculas nem acentos. `pao de queijo` encontra "Pão de Queijo". |
| **Preço** | O preço da mensagem é o **menor valor em `R$`** encontrado, nos formatos `R$ 3.499`, `R$3499`, `R$ 3.499,90`. Valores como `R$ 50 OFF` são ignorados. |
| **Preço máximo** | Se o item tem preço máximo, só avisa quando a mensagem tem preço **≤ máximo**. Mensagem sem preço não dispara itens com preço máximo. |
| **Duplicados** | Dentro de **12 h**, o mesmo item com o **mesmo preço** avisa uma vez só. Sem preço, a regra vale para o mesmo texto ignorando os links. |
| **Canais** | Só canais de transmissão; grupos são ignorados. Canais desligados não geram aviso. |

## Variáveis de ambiente

Arquivo `.env` na raiz (modelo em [.env.example](.env.example)):

| Variável | Obrigatória | Descrição |
|---|---|---|
| `API_ID` | sim | api_id do <https://my.telegram.org> |
| `API_HASH` | sim | api_hash do <https://my.telegram.org> |
| `BOT_TOKEN` | sim | token do @BotFather |
| `LOG_LEVEL` | não | `WARNING` (padrão), `INFO` ou `DEBUG`. Para depurar: `LOG_LEVEL=INFO docker compose up -d backend`. |
| `DB_PATH` | não | caminho do banco dentro do container (padrão `/data/promo.db`). As sessões do Telegram ficam na mesma pasta. |

## API HTTP

O backend escuta na porta 8000 dentro da rede do Docker. Por fora, use `http://localhost:8000/api/...` através do nginx.

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/items` | Lista os itens. |
| `POST` | `/api/items` | Cria um item. Corpo: `{"terms": "rtx 4070", "max_price": 3500}` (`max_price` pode ser `null`). Respostas: `201` criado, `400` inválido, `409` já existe. |
| `DELETE` | `/api/items/{id}` | Remove um item. |
| `GET` | `/api/channels` | Lista os canais (`id`, `title`, `enabled`). |
| `POST` | `/api/channels/{id}` | Liga/desliga o canal. |
| `GET` | `/api/hits` | Histórico (até 500, mais recentes primeiro). Filtros opcionais na query: `q` (texto), `item` (termo exato), `channel` (id), `min`/`max` (preço), `from`/`to` (unix timestamp), `after` (só ids maiores que este). |

Exemplo:

```sh
curl -X POST localhost:8000/api/items -d '{"terms":"air fryer","max_price":399.90}'
curl 'localhost:8000/api/hits?item=air%20fryer&max=350'
```

## Estrutura do projeto

```
.
├── backend/                 Python 3.12 + Telethon + SQLite
│   ├── main.py              ponto de entrada: cria o banco, sobe a API e o Telegram
│   ├── routes/api.py        rotas HTTP (/api/...)
│   ├── db/
│   │   ├── schema.sql       tabelas: items, channels, hits
│   │   ├── database.py      conexão e inicialização
│   │   └── repository.py    todas as queries SQL
│   ├── services/
│   │   ├── matcher.py       match de termos, leitura de preço, chave de duplicado
│   │   └── alerts.py        decide se uma mensagem gera aviso e grava no histórico
│   ├── bot/telegram.py      sessões da conta e do bot, /canais e botões
│   ├── tests/test_alerts.py self-check das regras
│   └── Dockerfile
├── frontend/                Vue 3 + Vite + Tailwind CSS 4
│   ├── src/
│   │   ├── App.vue          layout e abas
│   │   ├── components/      ItemsCard, ChannelsCard, HistoryCard
│   │   ├── services/        api.js (chamadas à API), notifications.js (notificações do navegador)
│   │   ├── utils/format.js  formatação de preço e data
│   │   └── style.css        tema (cores, fonte) e classes base
│   ├── nginx.conf           serve o build e repassa /api ao backend
│   └── Dockerfile           build com Node e servido por nginx
├── docker-compose.yml
├── .env.example
└── data/                    criada no 1º uso: banco e sessões (não versionada)
```

## Desenvolvimento

**Backend** sem Docker:

```sh
cd backend
python3 -m venv .venv && . .venv/bin/activate
pip install telethon==1.45.0
export $(grep -v '^#' ../.env | xargs) DB_PATH=../data/promo.db
python main.py                 # API em :8000
```

**Frontend** com hot reload:

```sh
cd frontend
npm install
npm run dev                    # http://localhost:5173, com /api repassado a localhost:8000
```

As cores ficam no `@theme` de [frontend/src/style.css](frontend/src/style.css) (`--color-neon`, `--color-ink`).

**Testes**, que cobrem match, leitura de preço, preço máximo, duplicados, canal desligado e filtros do histórico:

```sh
cd backend && python3 -m tests.test_alerts     # local
docker compose run --rm backend python -m tests.test_alerts   # no container
```

## Operação: logs, backup, atualização

```sh
docker compose logs -f backend        # acompanhar avisos e erros
docker compose restart backend        # reiniciar o monitor
docker compose down                   # parar tudo
git pull && docker compose up -d --build   # atualizar
```

A cada 5 min o log mostra uma linha de saúde, e cada aviso enviado gera uma linha `[aviso]`:

```
[status] últimos 5 min: 131 mensagens de canais, 0 avisos, 254 updates do Telegram (conexão viva se > 0)
```

**Backup**: copie a pasta `data/`, que contém `promo.db` (itens, canais e histórico) e as sessões. Para começar do zero, apague `data/promo.db`. Para trocar de conta, apague `data/session.session` e refaça o [primeiro login](#4-primeiro-login-só-uma-vez).

## Solução de problemas

| Sintoma | Causa / solução |
|---|---|
| O login pede "phone (or bot token)" | É o login da **sua conta**: digite o telefone com DDI. O token do bot é lido do `.env`. |
| Não recebo avisos | Envie `/start` para o bot e depois `/testar`. Confira se o canal está **ON**, se o preço máximo não está abaixo da oferta e se os termos aparecem do jeito que os canais escrevem ("lavadora" ≠ "máquina de lavar"). |
| Log mostra `0 updates do Telegram` | A conexão não está recebendo nada. Gere a imagem de novo (`docker compose up -d --build`) e veja se o Telethon está atualizado; a 1.36 parou de receber eventos. |
| Página mostra **API OFFLINE** | O backend caiu ou ainda está subindo: `docker compose ps` e `docker compose logs backend`. |
| Lista de canais vazia | O login ainda não foi feito ou não terminou. Ela é preenchida ao iniciar e a cada `/canais`. |
| `my.telegram.org` mostra "ERROR" | Desative bloqueadores ou VPN e tente de novo. |
| Mudei o código do backend e nada mudou | Gere a imagem de novo: `docker compose up -d --build`. |
| Erro de coluna ao subir após atualizar | O schema mudou: faça backup e apague `data/promo.db` (ele é recriado). |

## Segurança

- **`data/*.session` dá acesso total à sua conta do Telegram.** Não compartilhe, não versione (já está no `.gitignore`) e guarde os backups com cuidado.
- O `.env` contém `API_HASH` e `BOT_TOKEN`: também fica fora do git.
- A página **não tem login** e por isso só é publicada em `127.0.0.1:8000`. Não exponha na internet sem colocar autenticação na frente (ex.: proxy com senha).
- A conta é usada **só para ler** canais; quem envia mensagens é o bot.

## Limitações conhecidas

- **Match por substring**: `tv` também encontra "a**tv**". Use termos mais específicos.
- **Preço**: pega o menor `R$` da mensagem, então um "frete R$ 20" pode ser lido como preço.
- **Duplicados**: dois produtos diferentes do mesmo item com preço idêntico dentro de 12 h geram um aviso só.
- **`/canais` no bot** mostra até 100 canais (limite de botões do Telegram); na página não há limite.
- Itens não têm edição: para mudar o preço máximo, remova e cadastre de novo.

## Licença

[MIT](LICENSE)
