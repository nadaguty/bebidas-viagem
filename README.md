# Bebidas da Viagem

Organizador de bebidas para o grupo: cada um registra o que leva e a página soma litros, separa alcoólicas e sem álcool e mostra o total por tipo. Backend em Flask + SQLAlchemy, banco Postgres no Neon.

## 1. Banco no Neon
1. Crie um projeto em neon.com.
2. Clique em **Connect** e copie a connection string (use a versão *pooled*).
3. As tabelas são criadas sozinhas na primeira execução.

## 2. Rodar localmente
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # preencha DATABASE_URL
python app.py                                         # http://localhost:5000
```
Sem `DATABASE_URL`, o app usa um SQLite local (`bebidas.db`), útil para testar.

## 3. Publicar
**Vercel (recomendado):** suba o projeto no GitHub, importe o repositório em vercel.com/new (o `vercel.json` já posiciona a função na região `cle1` / `us-east-2`, junto ao banco do Neon) e adicione `DATABASE_URL` (e opcionalmente `ACCESS_CODE`) em *Environment Variables*.

**Render:** suba o projeto no GitHub, crie um *Blueprint* apontando para o repositório (ele lê o `render.yaml`) e preencha `DATABASE_URL` e `ACCESS_CODE` quando pedido.

**Railway:** crie um projeto a partir do repositório (usa o `Procfile`) e adicione `DATABASE_URL` e `ACCESS_CODE` em Variables.

## 4. Código de acesso
Se `ACCESS_CODE` estiver definido, a API só responde a quem abrir o link com o código: `https://seu-site/?codigo=SEU_CODIGO`. Mande esse link completo ao grupo. É uma barreira simples contra visitantes aleatórios, não um login: quem tiver o link tem acesso.

## API
| Método | Rota | Função |
|---|---|---|
| GET | `/api/bebidas` | lista os itens |
| POST | `/api/bebidas` | cria (`who`, `tipo`, `det`, `qtd`, `ml`) |
| DELETE | `/api/bebidas/<id>` | remove |
| GET | `/health` | verificação de saúde |

## Observações
- Na hospedagem gratuita, o primeiro acesso depois de um tempo parado pode demorar alguns segundos (o servidor e o Neon "acordam").
- A lista se atualiza sozinha a cada 10 segundos. Os tipos de bebida ficam em `TIPOS` no `app.py` e no `TIPOS` do `static/index.html`.
