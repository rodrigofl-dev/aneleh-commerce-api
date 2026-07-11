# 07 — Deployment

## Índice

- [1. Estrutura dos Containers](#1-estrutura-dos-containers)
- [2. Variáveis de Ambiente](#2-variáveis-de-ambiente)
- [3. Execução do Projeto](#3-execução-do-projeto)
- [4. Migrações](#4-migrações)
- [5. Dados de Demonstração (Seed)](#5-dados-de-demonstração-seed)
- [6. Testes](#6-testes)
- [7. Pipeline GitHub Actions](#7-pipeline-github-actions)
- [8. Boas Práticas](#8-boas-práticas)
- [9. Estrutura Final Esperada do Projeto](#9-estrutura-final-esperada-do-projeto)
- [10. Demonstração Pública (Opcional)](#10-demonstração-pública-opcional)

---

## 1. Estrutura dos Containers

O `docker-compose.yml` define cinco serviços:

| Serviço | Papel | Porta exposta |
|---|---|---|
| `api` | FastAPI (Uvicorn) | `8000` |
| `db` | MySQL | `3306` |
| `redis` | Cache, rate limiting, blacklist de JWT | `6379` |
| `rabbitmq` | Broker de mensagens (Celery) | `5672` (AMQP), `15672` (painel de gestão) |
| `worker` | Celery Worker | — (não exposto, consome da fila) |

```mermaid
flowchart TB
    subgraph docker-compose
        api[api: FastAPI]
        db[(db: MySQL)]
        redis[(redis: Redis)]
        rabbitmq[[rabbitmq: RabbitMQ]]
        worker[worker: Celery]
    end
    Client[Cliente HTTP] --> api
    api --> db
    api --> redis
    api --> rabbitmq
    rabbitmq --> worker
    worker --> db
    worker --> redis
```

Cada serviço declara um `healthcheck` no compose (ex: `mysqladmin ping` para o `db`, `redis-cli ping` para o `redis`), e o serviço `api` só sobe depois que `db`, `redis` e `rabbitmq` estiverem saudáveis (`depends_on` com `condition: service_healthy`).

---

## 2. Variáveis de Ambiente

Configuração via `pydantic-settings`, lida de um arquivo `.env` (não versionado — apenas um `.env.example` vai para o repositório).

| Variável | Exemplo | Descrição |
|---|---|---|
| `DATABASE_URL` | `mysql+pymysql://user:pass@db:3306/aneleh_commerce` | Conexão SQLAlchemy |
| `REDIS_URL` | `redis://redis:6379/0` | Conexão Redis |
| `RABBITMQ_URL` | `amqp://guest:guest@rabbitmq:5672//` | Broker do Celery |
| `JWT_SECRET_KEY` | (gerado, não versionado) | Chave de assinatura do JWT |
| `JWT_EXPIRATION_SECONDS` | `3600` | Tempo de vida do token |
| `ENVIRONMENT` | `development` \| `test` \| `production` | Controla comportamento sensível a ambiente (ex: logs mais verbosos em dev) |
| `RATE_LIMIT_PER_MINUTE` | `60` | Usado pelo rate limiting (NFR-04) |

> **Observação:** `JWT_SECRET_KEY` nunca deve ter um valor default hardcoded no código — a aplicação deve falhar ao subir se essa variável não existir em produção.

---

## 3. Execução do Projeto

```bash
# subir todo o ambiente
docker compose up -d

# rodar as migrações
docker compose exec api alembic upgrade head

# popular dados de demonstração
docker compose exec api python -m app.scripts.seed

# acompanhar logs da API
docker compose logs -f api
```

Após esses passos, a API está disponível em `http://localhost:8000/docs` (Swagger UI) e o painel do RabbitMQ em `http://localhost:15672`.

---

## 4. Migrações

Alembic gerencia o schema. Toda alteração de modelo (SQLAlchemy) precisa de uma migration correspondente antes de ser mergeada.

```bash
# gerar uma nova migration a partir dos models
docker compose exec api alembic revision --autogenerate -m "descrição da mudança"

# aplicar migrations pendentes
docker compose exec api alembic upgrade head
```

**Boas práticas:**
- Revisar sempre o arquivo gerado por `--autogenerate` — ele não é 100% confiável para todos os tipos de mudança (ex: renomear coluna costuma virar um `drop` + `add`, perdendo dado).
- Nunca editar uma migration que já foi aplicada em algum ambiente compartilhado — criar uma nova migration corretiva.

---

## 5. Dados de Demonstração (Seed)

Script (`app/scripts/seed.py`) que popula:

- Um usuário `admin` e um usuário `customer` de exemplo, com credenciais documentadas no `README.md` do repositório (não sensíveis, já que é um ambiente de demonstração).
- Categorias e produtos de exemplo suficientes para demonstrar listagem paginada e filtro por categoria.
- Estoque inicial coerente (produtos com estoque zero e com estoque disponível, para demonstrar ambos os casos).

O script deve ser **idempotente** — rodar mais de uma vez não deve gerar dados duplicados (checar existência antes de inserir).

---

## 6. Testes

Pytest, organizado espelhando a estrutura de `app/` (Package by Feature também nos testes).

| Tipo de teste | Escopo | Ferramenta |
|---|---|---|
| Unitário | Regras de negócio isoladas no `service`, sem banco real | Pytest + mocks/fakes de repository |
| Integração | Fluxo completo passando por banco real | Pytest + banco MySQL de teste (via `docker compose`, banco separado do de desenvolvimento) |

```bash
# rodar toda a suíte
docker compose exec api pytest

# rodar com cobertura
docker compose exec api pytest --cov=app --cov-report=term-missing
```

**Fluxos que precisam de teste de integração, no mínimo:**
- Registro → login → acesso a endpoint protegido → logout → token rejeitado.
- Criação de pedido debitando estoque corretamente (incluindo o caso de falha revertendo a transação).
- Checkout aprovado e recusado, incluindo devolução de estoque no caso recusado.

---

## 7. Pipeline GitHub Actions

Workflow único (`.github/workflows/ci.yml`), disparado em todo push e pull request:

```mermaid
flowchart LR
    Push[Push / PR] --> Lint[Flake8]
    Lint --> Format[Black --check]
    Format --> Tests[Pytest + coverage]
    Tests --> Status{Passou?}
    Status -->|Sim| Merge[Liberado para merge]
    Status -->|Não| Block[Bloqueia merge]
```

Os testes de integração do CI sobem um serviço MySQL descartável (via `services:` do próprio GitHub Actions), evitando depender do `docker-compose` completo dentro do runner.

---

## 8. Boas Práticas

- Nenhum segredo (chave JWT, senha de banco) commitado — sempre via variável de ambiente.
- `docker-compose.yml` de desenvolvimento não deve ser o mesmo usado em produção — se houver demonstração pública (seção 10), usar um compose/configuração separada, sem hot-reload e com `DEBUG=false`.
- Toda funcionalidade nova segue a ordem: requisito documentado (`02`) → teste escrito → implementação → migration (se aplicável) → documentação atualizada se algo mudou do planejado.
- Logs nunca contêm senha, hash de senha ou token JWT completo.

---

## 9. Estrutura Final Esperada do Projeto

```
aneleh-commerce-api/
├── app/
│   ├── main.py
│   ├── core/
│   ├── auth/
│   ├── users/
│   ├── categories/
│   ├── products/
│   ├── stock/
│   ├── cart/
│   ├── orders/
│   ├── checkout/
│   ├── audit/
│   ├── reports/
│   └── scripts/
│       └── seed.py
├── tests/
│   ├── auth/
│   ├── users/
│   ├── products/
│   ├── orders/
│   └── ...
├── alembic/
│   └── versions/
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── .github/
│   └── workflows/
│       └── ci.yml
├── requirements.txt (ou pyproject.toml)
└── README.md
```

---

## 10. Demonstração Pública (Opcional)

Não é um requisito do escopo (ver `01-project-charter.md`, seção 4), mas se você quiser que outras pessoas acessem o projeto sem precisar rodar Docker localmente, plataformas como Railway, Render ou Fly.io permitem subir o `docker-compose` (ou uma versão adaptada dele) com custo baixo ou gratuito para uso ocasional.

Pontos a considerar, caso decida seguir por esse caminho:
- Sem SLA — a demonstração pode ficar fora do ar sem aviso, o que é aceitável para um projeto de portfólio.
- Dados de demonstração (seed) tornam-se ainda mais importantes, já que a pessoa acessando não vai popular o catálogo manualmente.
- Vale desligar o Swagger `/docs` em produção real, mas para uma demonstração de portfólio, mantê-lo ativo é geralmente desejável — é a própria "vitrine" da API.

---

Este é o último documento da documentação inicial. A partir daqui, o guia de desenvolvimento é: seguir `06-development-roadmap.md` fase a fase, consultando `02` a `05` conforme a dependência de cada funcionalidade.
