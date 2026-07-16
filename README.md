# Aneleh Commerce API

> API RESTful que simula o backend de um e-commerce de ponta a ponta — do cadastro do usuário ao checkout simulado — construída como projeto de portfólio em Python/FastAPI.

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![Fases](https://img.shields.io/badge/roadmap-2%2F11%20fases%20conclu%C3%ADdas-blue)
![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.139-009688)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Sobre o projeto

Não existe frontend aqui — o sistema inteiro é consumido via HTTP e documentado automaticamente via Swagger/OpenAPI. A proposta não é cobrir a maior quantidade possível de funcionalidades de e-commerce, e sim um recorte pequeno e executado com profundidade: autenticação e autorização de verdade, controle de estoque transacional, cache, mensageria e processamento assíncrono — as peças que aparecem em qualquer backend de produção, implementadas com as decisões de design explicadas, não copiadas de tutorial.

O projeto foi conduzido como se fosse um contrato formal entre cliente e desenvolvedor (mesmo sendo a mesma pessoa nos dois papéis): requisitos escritos antes do código, critérios de aceite por funcionalidade, e uma decisão de arquitetura só entra no repositório depois de justificada. Essa documentação completa está disponível na pasta [`/doc`](./doc).

---

## Status atual do desenvolvimento

O projeto avança em fases, cada uma com *definition of done* própria — nada é considerado "pronto" só porque o código roda; precisa satisfazer os critérios de aceite documentados.

| # | Fase | Status |
|---|---|---|
| 0 | Fundação do projeto (Docker, CI, lint, health checks) | ✅ Concluída |
| 1 | Autenticação e RBAC (JWT, papéis, blacklist) | ✅ Concluída |
| 2 | Catálogo (categorias e produtos) | ⏳ Próxima |
| 3 | Cache do catálogo (Redis) | ⬜ Planejada |
| 4 | Estoque e auditoria | ⬜ Planejada |
| 5 | Carrinho | ⬜ Planejada |
| 6 | Pedidos | ⬜ Planejada |
| 7 | Checkout simulado | ⬜ Planejada |
| 8 | Processamento assíncrono (Celery/RabbitMQ) | ⬜ Planejada |
| 9 | Observabilidade e robustez | ⬜ Planejada |
| 10 | Deploy e polimento final | ⬜ Planejada |

Detalhe completo de cada fase, com checklist e critérios de aceite, em [`doc/06-development-roadmap.md`](./doc/06-development-roadmap.md).

---

## O que já funciona

- **Registro e login** com JWT, senha com hash via bcrypt.
- **Logout com blacklist no Redis** — um token pode ser invalidado antes da expiração natural, sem precisar manter estado de sessão no banco.
- **RBAC por dependency do FastAPI**, com o papel do usuário revalidado no banco a cada requisição (não confia apenas no papel embutido no JWT) — uma mudança de papel feita por um admin tem efeito imediato.
- **Gestão de usuários e papéis** (`/users/me`, alteração de papel por admin, proteção contra remover o último admin do sistema).
- **Ambiente 100% via Docker** — API, MySQL, Redis e RabbitMQ sobem juntos com healthcheck, sem instalação manual de dependência na máquina local.
- **CI no GitHub Actions** rodando lint (Flake8), formatação (Black) e testes a cada push.

## Em desenvolvimento

Catálogo (categorias/produtos), cache de leitura, controle de estoque com auditoria, carrinho, pedidos com preço congelado, checkout simulado e as tarefas assíncronas (e-mail, relatórios) via Celery. A ordem e as dependências entre essas fases seguem o roadmap linkado acima — nenhuma é implementada fora de ordem, mesmo quando pareceria possível adiantar algo.

---

## Stack técnica

| Camada | Tecnologia | Por quê |
|---|---|---|
| API | FastAPI + Pydantic | Tipagem, validação automática e documentação OpenAPI gerada de graça |
| Banco de dados | MySQL + SQLAlchemy 2.0 | Modelagem relacional com integridade real (constraints, FKs) |
| Migrações | Alembic | Schema versionado, sem alteração manual de tabela |
| Cache / sessão | Redis | Cache de catálogo, rate limiting e blacklist de JWT |
| Mensageria | RabbitMQ + Celery | Broker AMQP dedicado (com dead-letter queue e retry), em vez do Redis como broker — decisão registrada em `doc/03-architecture.md`, seção 8 |
| Infra | Docker + docker-compose | Ambiente reproduzível com um único comando |
| Qualidade | Pytest, Black, Flake8, GitHub Actions | Testes unitários e de integração, lint e formatação obrigatórios no CI |

## Algumas decisões de arquitetura que valem destacar

- **Package by Feature em vez de Clean Architecture clássica.** O código é organizado por domínio de negócio (`users/`, `products/`, `orders/`...), cada um com suas próprias camadas internas (`router` → `service` → `repository`). As 4 camadas clássicas de Clean Architecture (Entities, Use Cases, Interface Adapters, Frameworks & Drivers) foram avaliadas e descartadas para este projeto: as regras de negócio aqui não têm complexidade suficiente para justificar uma Use Case isolada por verbo — o custo seria cerimônia sem ganho real de clareza. O princípio central (regra de negócio isolada, sem se misturar com FastAPI/SQLAlchemy) foi mantido dentro da camada `service`.
- **`HTTPBearer` em vez de `OAuth2PasswordBearer`.** O segundo obrigaria o login a aceitar `application/x-www-form-urlencoded` com um campo fixo `username`, um contrato emprestado do fluxo OAuth2 que não existe de verdade aqui (não há authorization server nem terceiros envolvidos). `HTTPBearer` extrai o token e deixa a validação do JWT inteiramente sob controle da aplicação — e o botão "Authorize" do Swagger continua funcionando normalmente.
- **Estoque como coluna do produto, não uma tabela à parte.** O histórico de alterações já é coberto pela tabela de auditoria (toda alteração de estoque gera uma entrada). Uma tabela extra só para "estoque atual" duplicaria informação sem necessidade.

Todas as decisões de arquitetura — incluindo as que não couberam aqui — estão documentadas e justificadas em [`doc/03-architecture.md`](./doc/03-architecture.md).

---

## Como rodar o projeto localmente

```bash
# 1. clonar o repositório e configurar variáveis de ambiente
cp env.example .env

# 2. subir o ambiente completo (API, MySQL, Redis, RabbitMQ)
docker compose up -d

# 3. rodar as migrações
docker compose exec server alembic upgrade head

# 4. popular dados de demonstração (idempotente)
docker compose exec server python -m app.scripts.seed
```

Depois disso:
- API + Swagger UI: **http://localhost:8000/docs**
- Painel do RabbitMQ: **http://localhost:15672**

## Testes

```bash
# suíte completa
docker compose exec server pytest

# com cobertura
docker compose exec server pytest --cov=app --cov-report=term-missing
```

---

## Documentação completa

Toda decisão técnica deste projeto foi documentada antes de ser implementada. Os documentos abaixo estão em [`/doc`](./doc) e formam a fonte da verdade do projeto — este README é só a porta de entrada:

| Documento | Conteúdo |
|---|---|
| [`01-project-charter.md`](./doc/01-project-charter.md) | Objetivo, escopo, fora do escopo, riscos |
| [`02-requirements.md`](./doc/02-requirements.md) | Requisitos funcionais e não funcionais por módulo |
| [`03-architecture.md`](./doc/03-architecture.md) | Arquitetura, autenticação, RBAC, Redis, RabbitMQ/Celery |
| [`04-database.md`](./doc/04-database.md) | Modelagem de entidades e diagrama ER |
| [`05-api-design.md`](./doc/05-api-design.md) | Contrato completo de endpoints |
| [`06-development-roadmap.md`](./doc/06-development-roadmap.md) | Fases de implementação com *definition of done* |
| [`07-deployment.md`](./doc/07-deployment.md) | Docker, variáveis de ambiente, CI, testes |

---

## Autor

Projeto pessoal desenvolvido para consolidar e demonstrar prática de arquitetura backend em Python. Feedback e sugestões são bem-vindos.
