# 06 — Development Roadmap

## Índice

- [Como usar este roadmap](#como-usar-este-roadmap)
- [Fase 0 — Fundação do Projeto](#fase-0--fundação-do-projeto)
- [Fase 1 — Autenticação e RBAC](#fase-1--autenticação-e-rbac)
- [Fase 2 — Catálogo (Categorias e Produtos)](#fase-2--catálogo-categorias-e-produtos)
- [Fase 3 — Cache do Catálogo](#fase-3--cache-do-catálogo)
- [Fase 4 — Estoque e Auditoria](#fase-4--estoque-e-auditoria)
- [Fase 5 — Carrinho](#fase-5--carrinho)
- [Fase 6 — Pedidos](#fase-6--pedidos)
- [Fase 7 — Checkout Simulado](#fase-7--checkout-simulado)
- [Fase 8 — Processamento Assíncrono](#fase-8--processamento-assíncrono)
- [Fase 9 — Observabilidade e Robustez](#fase-9--observabilidade-e-robustez)
- [Fase 10 — Deploy e Polimento Final](#fase-10--deploy-e-polimento-final)

---

## Como usar este roadmap

Cada fase só começa quando a anterior atinge sua **Definition of Done**. As fases seguem a ordem de dependência real do sistema — não pule fases mesmo que pareça possível implementar algo "adiantado". Dentro de uma fase, a ordem interna do checklist também importa.

Não há prazos. O critério de avanço é sempre: **os critérios de aceite da fase estão satisfeitos e testados?**

---

## Fase 0 — Fundação do Projeto

**Objetivo:** ter o esqueleto do projeto rodando via Docker, sem nenhuma funcionalidade de negócio ainda.

**Funcionalidades:** nenhuma de negócio — apenas infraestrutura.

**Dependências:** nenhuma.

**Checklist:**
- [x] `docker-compose.yml` com API, MySQL, Redis e RabbitMQ subindo juntos.
- [x] FastAPI respondendo em uma rota de teste.
- [x] Estrutura de pastas por Package by Feature criada (mesmo que módulos estejam vazios).
- [x] Alembic configurado e rodando a primeira migration (mesmo que vazia).
- [x] Black e Flake8 configurados e rodando localmente.
- [x] Pipeline básico do GitHub Actions (lint + format check) rodando em um push de teste.
- [x] Endpoints `/health` e `/ready` implementados (NFR-05).

**Definition of Done:** `docker-compose up` sobe o ambiente inteiro sem erro, `/health` e `/ready` retornam `200`, e o CI passa em um push trivial.

**Critérios de aceite:** ambiente reproduzível do zero por qualquer pessoa que clonar o repositório e rodar um único comando.

**Ordem sugerida:** Docker → FastAPI mínimo → MySQL/Alembic → Redis/RabbitMQ no compose → lint/format → CI → health checks.

---

## Fase 1 — Autenticação e RBAC

**Objetivo:** ter um sistema de login funcional com controle de acesso por papel.

**Funcionalidades:** RF-AUTH-01 a RF-AUTH-04, RF-USERS-01 a RF-USERS-03.

**Dependências:** Fase 0.

**Checklist:**
- [ ] Tabelas `roles` e `users` migradas.
- [ ] Registro de usuário (papel `customer` por padrão).
- [ ] Login com JWT + `HTTPBearer`.
- [ ] Logout com blacklist no Redis.
- [ ] Dependency de checagem de papel (`require_role`).
- [ ] Endpoints de perfil (`/users/me`) e gestão de papel (`admin`).
- [ ] Seed inicial: pelo menos um usuário `admin` criado via script/migration.

**Definition of Done:** é possível registrar, logar, acessar um endpoint protegido, deslogar e confirmar que o token deslogado é rejeitado — tudo via Swagger.

**Critérios de aceite:** os critérios de aceite de cada requisito (RF-AUTH-01 a RF-USERS-03) em `02-requirements.md` estão satisfeitos.

**Ordem sugerida:** modelo de dados → registro → login → dependency de autenticação → dependency de autorização → logout/blacklist → gestão de papel.

---

## Fase 2 — Catálogo (Categorias e Produtos)

**Objetivo:** CRUD completo de categorias e produtos, sem cache ainda.

**Funcionalidades:** RF-CATALOG-01, RF-CATALOG-02.

**Dependências:** Fase 1 (endpoints administrativos exigem RBAC).

**Checklist:**
- [ ] Tabela `categories` e `products` migradas.
- [ ] CRUD de categoria com soft delete e bloqueio se houver produto vinculado.
- [ ] CRUD de produto com validação de preço e vínculo obrigatório a categoria.
- [ ] Seed com categorias e produtos de exemplo (NFR-09).

**Definition of Done:** `admin` consegue criar categoria, criar produto vinculado, e o sistema recusa corretamente os casos inválidos (categoria duplicada, produto sem categoria, preço inválido).

**Critérios de aceite:** critérios de RF-CATALOG-01 e RF-CATALOG-02 satisfeitos.

**Ordem sugerida:** categorias → produtos (dependem de categoria existente).

---

## Fase 3 — Cache do Catálogo

**Objetivo:** listagem e detalhe de produto servidos via Redis, com invalidação correta.

**Funcionalidades:** RF-CATALOG-03, RF-CATALOG-04.

**Dependências:** Fase 2.

**Checklist:**
- [ ] Listagem de produtos paginada (NFR-02) com cache Redis.
- [ ] Detalhe de produto com cache individual.
- [ ] Invalidação de cache ao atualizar produto (detalhe + listagens afetadas).
- [ ] Teste manual: alterar produto e confirmar que o cache reflete a mudança na próxima consulta.

**Definition of Done:** é possível demonstrar, via log ou header de resposta, que a segunda consulta idêntica veio do cache, e que uma alteração invalida o cache corretamente.

**Critérios de aceite:** critérios de RF-CATALOG-03 e RF-CATALOG-04 satisfeitos.

**Ordem sugerida:** cache de listagem → cache de detalhe → invalidação em cascata na atualização.

---

## Fase 4 — Estoque e Auditoria

**Objetivo:** ajuste de estoque controlado, com toda alteração relevante registrada em auditoria.

**Funcionalidades:** RF-STOCK-01, RF-AUDIT-01.

**Dependências:** Fase 2 (produto precisa existir), Fase 8 parcialmente antecipada (auditoria é gravada de forma assíncrona — se a Fase 8 ainda não estiver pronta, pode-se gravar de forma síncrona nesta fase e migrar para assíncrono depois, documentando essa transição).

**Checklist:**
- [ ] Tabela `audit_log` migrada.
- [ ] Endpoint de ajuste de estoque com bloqueio de estoque negativo.
- [ ] Toda alteração de estoque gera entrada de auditoria.
- [ ] Consulta de auditoria (`admin`) com filtro por entidade.

**Definition of Done:** todo ajuste de estoque (positivo ou negativo) aparece consultável em `/audit-log`, e o sistema nunca permite estoque negativo.

**Critérios de aceite:** critérios de RF-STOCK-01 e RF-AUDIT-01 satisfeitos.

**Ordem sugerida:** modelo de auditoria → endpoint de ajuste de estoque → consulta de auditoria.

---

## Fase 5 — Carrinho

**Objetivo:** carrinho funcional por usuário, com cálculo de subtotal em tempo real.

**Funcionalidades:** RF-CART-01 a RF-CART-03.

**Dependências:** Fase 1 (usuário autenticado), Fase 2 (produto existente).

**Checklist:**
- [ ] Tabelas `carts` e `cart_items` migradas.
- [ ] Adicionar item (soma quantidade se já existir).
- [ ] Atualizar/remover item (quantidade zero remove).
- [ ] Consulta do carrinho com subtotal calculado na hora.
- [ ] Validação de quantidade contra estoque disponível.

**Definition of Done:** um usuário consegue montar um carrinho completo, alterar quantidades e ver o subtotal refletir alterações de preço do catálogo em tempo real.

**Critérios de aceite:** critérios de RF-CART-01 a RF-CART-03 satisfeitos.

---

## Fase 6 — Pedidos

**Objetivo:** transformar carrinho em pedido de forma atômica, com preço congelado.

**Funcionalidades:** RF-STOCK-02, RF-ORDERS-01, RF-ORDERS-02.

**Dependências:** Fase 4 (estoque), Fase 5 (carrinho).

**Checklist:**
- [ ] Tabelas `orders` e `order_items` migradas.
- [ ] Criação de pedido como transação única (debita estoque + grava pedido + esvazia carrinho).
- [ ] Preço congelado em `order_items.unit_price`.
- [ ] Máquina de estados de status implementada e validada no `service` (não apenas enum solto).
- [ ] Listagem de pedidos (própria para `customer`, todas para `admin`).

**Definition of Done:** um pedido criado a partir de um carrinho válido debita o estoque corretamente, congela o preço, esvazia o carrinho, e uma tentativa de pedido com estoque insuficiente é rejeitada sem efeitos colaterais parciais.

**Critérios de aceite:** critérios de RF-STOCK-02, RF-ORDERS-01 e RF-ORDERS-02 satisfeitos.

---

## Fase 7 — Checkout Simulado

**Objetivo:** simular aprovação/recusa de pagamento, incluindo devolução de estoque em caso de recusa.

**Funcionalidades:** RF-CHECKOUT-01.

**Dependências:** Fase 6.

**Checklist:**
- [ ] Endpoint de checkout implementado com resultado simulado (aprovado/recusado).
- [ ] Pagamento aprovado → status `pago`.
- [ ] Pagamento recusado → status `cancelado` **e** devolução do estoque debitado (decisão registrada em `03-architecture.md`, seção 10).
- [ ] Bloqueio de checkout em pedido que não está em `pagamento_pendente`.

**Definition of Done:** os dois caminhos (aprovado e recusado) são demonstráveis via Swagger, com o estoque se comportando corretamente em ambos.

**Critérios de aceite:** critérios de RF-CHECKOUT-01 satisfeitos.

---

## Fase 8 — Processamento Assíncrono

**Objetivo:** mover para Celery/RabbitMQ tudo que faz sentido não bloquear a resposta ao cliente.

**Funcionalidades:** módulo transversal ASYNC (`02-requirements.md`).

**Dependências:** Fase 4 (auditoria, se ainda síncrona, migra pra cá), Fase 6 (pedido criado dispara e-mail).

**Checklist:**
- [ ] Worker Celery configurado e conectado ao RabbitMQ.
- [ ] Envio de e-mail (mock) disparado após criação de pedido.
- [ ] Gravação de auditoria migrada para assíncrona, se ainda não estiver.
- [ ] Geração de relatório "vendas por período" e "produtos mais vendidos" (RF assíncronos, endpoints `POST/GET /reports`).
- [ ] Fluxo de retry e dead-letter queue configurado (ver `03-architecture.md`, seção 9).

**Definition of Done:** é possível disparar uma tarefa assíncrona, ver o worker processá-la, e consultar o resultado (relatório) depois de pronto.

**Critérios de aceite:** os fluxos assíncronos descritos em `02-requirements.md` e `03-architecture.md` funcionam de ponta a ponta.

---

## Fase 9 — Observabilidade e Robustez

**Objetivo:** deixar o sistema com os requisitos não funcionais que não são "funcionalidade" mas fazem parte de uma API profissional.

**Funcionalidades:** NFR-03 (formato de erro), NFR-04 (rate limiting), NFR-06 (logging estruturado).

**Dependências:** todas as fases anteriores (esses requisitos atravessam o sistema inteiro).

**Checklist:**
- [ ] Formato único de erro aplicado consistentemente em todos os endpoints.
- [ ] Rate limiting implementado nos endpoints públicos (login, listagem de produtos).
- [ ] Logging estruturado (JSON) com identificador de requisição.
- [ ] Revisão geral: nenhum endpoint retorna erro fora do padrão definido em `05-api-design.md`.

**Definition of Done:** uma bateria de testes manuais (ou automatizados) confirma que erros, rate limit e logs seguem o padrão documentado em todos os módulos.

---

## Fase 10 — Deploy e Polimento Final

**Objetivo:** projeto pronto para ser demonstrado e avaliado por terceiros.

**Funcionalidades:** nenhuma nova — consolidação.

**Dependências:** todas as fases anteriores.

**Checklist:**
- [ ] Suíte de testes Pytest cobrindo os principais fluxos (ver `07-deployment.md`).
- [ ] Pipeline de CI completo (lint, format, testes) obrigatório antes de merge.
- [ ] Script de seed revisado e documentado (dados de demonstração completos, NFR-09).
- [ ] README do repositório com instruções de execução local.
- [ ] (Opcional) Avaliação de viabilidade de uma demonstração pública (ver `07-deployment.md`).

**Definition of Done:** qualquer pessoa consegue clonar o repositório, subir o ambiente, rodar o seed e testar o fluxo completo (cadastro → login → catálogo → carrinho → pedido → checkout) sem precisar ler o código-fonte primeiro.

---

**Próximo documento:** `07-deployment.md` — Docker, variáveis de ambiente, execução do projeto, testes, pipeline de CI e estrutura final esperada.
