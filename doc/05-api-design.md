# 05 — API Design

## Índice

- [1. Convenções Gerais](#1-convenções-gerais)
- [2. Autenticação (AUTH)](#2-autenticação-auth)
- [3. Usuários (USERS)](#3-usuários-users)
- [4. Categorias (CATEGORIES)](#4-categorias-categories)
- [5. Produtos e Estoque (PRODUCTS)](#5-produtos-e-estoque-products)
- [6. Carrinho (CART)](#6-carrinho-cart)
- [7. Pedidos e Checkout (ORDERS)](#7-pedidos-e-checkout-orders)
- [8. Auditoria (AUDIT)](#8-auditoria-audit)
- [9. Relatórios (REPORTS)](#9-relatórios-reports)
- [10. Health Check](#10-health-check)

---

## 1. Convenções Gerais

**Base path:** todas as rotas de negócio ficam sob `/api/v1`.

**Autenticação:** header `Authorization: Bearer <token>`, validado via `HTTPBearer` (ver `03-architecture.md`, seção 6). Endpoints marcados como "Pública" não exigem esse header.

**Paginação:** listagens aceitam `limit` (default 20, máximo 100) e `offset` (default 0). Resposta paginada sempre no formato:

```json
{
  "items": [ ... ],
  "total": 137,
  "limit": 20,
  "offset": 0
}
```

**Formato de erro (padrão único, NFR-03):**

```json
{
  "error": {
    "code": "PRODUCT_OUT_OF_STOCK",
    "message": "Quantidade solicitada excede o estoque disponível.",
    "details": { "product_id": 42, "available": 3 }
  }
}
```

- `401` — não autenticado (token ausente, inválido, expirado ou na blacklist).
- `403` — autenticado, mas sem permissão para a ação (papel incompatível).
- `404` — recurso não encontrado.
- `409` — conflito de regra de negócio (ex: e-mail duplicado, estoque insuficiente).
- `422` — erro de validação de schema (tratado automaticamente pelo FastAPI/Pydantic).

---

## 2. Autenticação (AUTH)

| Endpoint | Método | Rota | Auth | Permissão |
|---|---|---|---|---|
| Registro | POST | `/api/v1/auth/register` | Pública | — |
| Login | POST | `/api/v1/auth/login` | Pública | — |
| Logout | POST | `/api/v1/auth/logout` | Requerida | qualquer papel |

### POST `/api/v1/auth/register`
- **Objetivo:** criar uma conta com papel `customer`.
- **Parâmetros (body):** `name`, `email`, `password`.
- **Resposta esperada:** `201`, dados do usuário criado (sem `password_hash`).
- **Erros possíveis:** `409 EMAIL_ALREADY_EXISTS`.

### POST `/api/v1/auth/login`
- **Objetivo:** autenticar e obter um JWT.
- **Parâmetros (body):** `email`, `password`.
- **Resposta esperada:** `200`, `{ "access_token": "...", "token_type": "bearer", "expires_in": 3600, "user": { ... UserOut ... } }`. O usuário é incluído na resposta do login (decisão tomada na Fase 1) para evitar que o cliente precise chamar `GET /users/me` logo em seguida só para saber quem acabou de logar.
- **Erros possíveis:** `401 INVALID_CREDENTIALS` (genérico, não revela se o e-mail existe).

### POST `/api/v1/auth/logout`
- **Objetivo:** invalidar o token atual antes da expiração natural.
- **Parâmetros:** nenhum (token vem do header).
- **Resposta esperada:** `204`.
- **Erros possíveis:** `401` se token já inválido.

---

## 3. Usuários (USERS)

| Endpoint | Método | Rota | Auth | Permissão |
|---|---|---|---|---|
| Meu perfil | GET | `/api/v1/users/me` | Requerida | qualquer papel |
| Atualizar meu perfil | PATCH | `/api/v1/users/me` | Requerida | qualquer papel |
| Consultar usuário por ID | GET | `/api/v1/users/{id}` | Requerida | `admin` |
| Alterar papel de usuário | PATCH | `/api/v1/users/{id}/role` | Requerida | `admin` |

### GET `/api/v1/users/me`
- **Resposta esperada:** `200`, dados do próprio usuário.

### PATCH `/api/v1/users/me`
- **Parâmetros (body, todos opcionais):** `name`, `email`, `password`.
- **Resposta esperada:** `200`, usuário atualizado.
- **Erros possíveis:** `409 EMAIL_ALREADY_EXISTS`. Troca de senha invalida tokens anteriores (ver RF-USERS-02).

### GET `/api/v1/users/{id}`
- **Resposta esperada:** `200`, dados do usuário consultado.
- **Erros possíveis:** `403` se quem consulta não for `admin`; `404` se usuário não existir.

### PATCH `/api/v1/users/{id}/role`
- **Parâmetros (body):** `role` (`admin` | `customer`).
- **Resposta esperada:** `200`, usuário com papel atualizado.
- **Erros possíveis:** `409 LAST_ADMIN_CANNOT_BE_DEMOTED` (RF-USERS-03).

---

## 4. Categorias (CATEGORIES)

| Endpoint | Método | Rota | Auth | Permissão |
|---|---|---|---|---|
| Criar categoria | POST | `/api/v1/categories` | Requerida | `admin` |
| Listar categorias | GET | `/api/v1/categories` | Pública | — |
| Detalhe da categoria | GET | `/api/v1/categories/{id}` | Pública | — |
| Atualizar categoria | PATCH | `/api/v1/categories/{id}` | Requerida | `admin` |
| Excluir categoria | DELETE | `/api/v1/categories/{id}` | Requerida | `admin` |

### POST `/api/v1/categories`
- **Parâmetros (body):** `name`.
- **Resposta esperada:** `201`.
- **Erros possíveis:** `409 CATEGORY_ALREADY_EXISTS`.

### GET `/api/v1/categories`
- **Parâmetros (query):** `limit`, `offset`.
- **Resposta esperada:** `200`, lista paginada.

### DELETE `/api/v1/categories/{id}`
- **Regra:** exclusão real (não é soft delete — `active` não tem relação com exclusão, ver `04-database.md`).
- **Resposta esperada:** `204`.
- **Erros possíveis:** `409 CATEGORY_HAS_PRODUCTS` se houver produtos vinculados (RF-CATALOG-01). Bloqueio reforçado no banco via `ON DELETE RESTRICT` na FK `products.category_id`.

### PATCH `/api/v1/categories/{id}`
- **Parâmetros (body):** `name`.
- **Objetivo:** atualizar nome.
- **Resposta esperada:** `200`, categoria atualizada.
- **Erros possíveis:** `409 CATEGORY_ALREADY_EXISTS` (se `name` colidir com outra categoria); `404` se categoria não existir.

---

## 5. Produtos e Estoque (PRODUCTS)

| Endpoint | Método | Rota | Auth | Permissão |
|---|---|---|---|---|
| Criar produto | POST | `/api/v1/products` | Requerida | `admin` |
| Listar produtos | GET | `/api/v1/products` | Pública | — |
| Detalhe do produto | GET | `/api/v1/products/{id}` | Pública | — |
| Atualizar produto | PATCH | `/api/v1/products/{id}` | Requerida | `admin` |
| Desativar produto | DELETE | `/api/v1/products/{id}` | Requerida | `admin` |
| Ajustar estoque | PATCH | `/api/v1/products/{id}/stock` | Requerida | `admin` |

### POST `/api/v1/products`
- **Parâmetros (body):** `name`, `description`, `price`, `category_id`.
- **Resposta esperada:** `201`, produto criado com `stock_quantity = 0`.
- **Erros possíveis:** `422` (preço ≤ 0), `404 CATEGORY_NOT_FOUND`.

### GET `/api/v1/products`
- **Parâmetros (query):** `limit`, `offset`, `category_id` (opcional), `include_unavailable` (opcional, default `false`).
- **Resposta esperada:** `200`, lista paginada. Servida via cache Redis (RF-CATALOG-03).

### GET `/api/v1/products/{id}`
- **Resposta esperada:** `200`. Servida via cache Redis (RF-CATALOG-04).
- **Erros possíveis:** `404`.

### PATCH `/api/v1/products/{id}`
- **Resposta esperada:** `200`. Invalida o cache de detalhe do produto e da(s) listagem(ns) que o incluem.

### PATCH `/api/v1/products/{id}/stock`
- **Objetivo:** ajuste manual de estoque (reposição, correção).
- **Parâmetros (body):** `quantity_change` (inteiro, positivo ou negativo), `reason`.
- **Resposta esperada:** `200`, estoque atualizado. Gera entrada em auditoria (RF-STOCK-01).
- **Erros possíveis:** `409 STOCK_CANNOT_BE_NEGATIVE`.

---

## 6. Carrinho (CART)

Todos os endpoints operam sobre o carrinho do próprio usuário autenticado — não existe carrinho de terceiros.

| Endpoint | Método | Rota | Auth | Permissão |
|---|---|---|---|---|
| Consultar carrinho | GET | `/api/v1/cart` | Requerida | qualquer papel |
| Adicionar item | POST | `/api/v1/cart/items` | Requerida | qualquer papel |
| Atualizar quantidade | PATCH | `/api/v1/cart/items/{product_id}` | Requerida | qualquer papel |
| Remover item | DELETE | `/api/v1/cart/items/{product_id}` | Requerida | qualquer papel |

### GET `/api/v1/cart`
- **Resposta esperada:** `200`, itens do carrinho com subtotal calculado na consulta (RF-CART-03).

### POST `/api/v1/cart/items`
- **Parâmetros (body):** `product_id`, `quantity`.
- **Resposta esperada:** `201` ou `200` se o item já existia (quantidade somada).
- **Erros possíveis:** `409 INSUFFICIENT_STOCK`.

### PATCH `/api/v1/cart/items/{product_id}`
- **Parâmetros (body):** `quantity` (zero remove o item, RF-CART-02).
- **Resposta esperada:** `200`.

### DELETE `/api/v1/cart/items/{product_id}`
- **Resposta esperada:** `204`.

---

## 7. Pedidos e Checkout (ORDERS)

| Endpoint | Método | Rota | Auth | Permissão |
|---|---|---|---|---|
| Criar pedido | POST | `/api/v1/orders` | Requerida | qualquer papel |
| Listar pedidos | GET | `/api/v1/orders` | Requerida | qualquer papel (escopo variável, ver abaixo) |
| Detalhe do pedido | GET | `/api/v1/orders/{id}` | Requerida | dono do pedido ou `admin` |
| Processar checkout | POST | `/api/v1/orders/{id}/checkout` | Requerida | dono do pedido |

### POST `/api/v1/orders`
- **Objetivo:** transformar o carrinho atual em pedido (RF-ORDERS-01).
- **Resposta esperada:** `201`, pedido com status `pagamento_pendente`.
- **Erros possíveis:** `409 CART_EMPTY`, `409 INSUFFICIENT_STOCK`.

### GET `/api/v1/orders`
- **Parâmetros (query):** `limit`, `offset`, `status` (opcional).
- **Regra:** `customer` vê apenas os próprios pedidos; `admin` vê todos e pode filtrar por `user_id`.
- **Resposta esperada:** `200`, lista paginada.

### GET `/api/v1/orders/{id}`
- **Resposta esperada:** `200`, detalhe com itens e status.
- **Erros possíveis:** `403` se não for o dono nem `admin`; `404`.

### POST `/api/v1/orders/{id}/checkout`
- **Objetivo:** simular o processamento de pagamento (RF-CHECKOUT-01).
- **Parâmetros (body):** nenhum obrigatório — resultado é determinístico/simulado internamente.
- **Resposta esperada:** `200`, pedido com status `pago` ou `cancelado`.
- **Regra:** se recusado, estoque debitado na criação é devolvido (ver `03-architecture.md`, seção 10).
- **Erros possíveis:** `409 ORDER_NOT_PAYABLE` se o pedido não estiver em `pagamento_pendente`.

---

## 8. Auditoria (AUDIT)

| Endpoint | Método | Rota | Auth | Permissão |
|---|---|---|---|---|
| Consultar log de auditoria | GET | `/api/v1/audit-log` | Requerida | `admin` |

### GET `/api/v1/audit-log`
- **Parâmetros (query):** `limit`, `offset`, `entity_type` (opcional), `entity_id` (opcional).
- **Resposta esperada:** `200`, lista paginada de entradas de auditoria.

---

## 9. Relatórios (REPORTS)

Relatórios são gerados de forma assíncrona (Celery) e consultados depois de prontos — não é um endpoint de resposta imediata (ver `02-requirements.md`, seção ASYNC).

| Endpoint | Método | Rota | Auth | Permissão |
|---|---|---|---|---|
| Solicitar relatório | POST | `/api/v1/reports` | Requerida | `admin` |
| Consultar status/resultado | GET | `/api/v1/reports/{id}` | Requerida | `admin` |

### POST `/api/v1/reports`
- **Parâmetros (body):** `type` (`sales_by_period` | `top_products`), `date_from`, `date_to`.
- **Resposta esperada:** `202`, `{ "report_id": "...", "status": "processing" }`.

### GET `/api/v1/reports/{id}`
- **Resposta esperada:** `200`, `{ "status": "processing" | "done" | "failed", "result": { ... } | null }`.
- **Erros possíveis:** `404`.

---

## 10. Health Check

| Endpoint | Método | Rota | Auth | Permissão |
|---|---|---|---|---|
| Liveness | GET | `/health` | Pública | — |
| Readiness | GET | `/ready` | Pública | — |

### GET `/health`
- **Objetivo:** indicar que o processo da API está de pé.
- **Resposta esperada:** `200`, `{ "status": "ok" }`.

### GET `/ready`
- **Objetivo:** indicar que as dependências externas (MySQL, Redis, RabbitMQ) estão acessíveis.
- **Resposta esperada:** `200` se todas as conexões estiverem saudáveis; `503` caso alguma falhe, com detalhe de qual dependência falhou.

---

**Próximo documento:** `06-development-roadmap.md` — divisão do projeto em fases de implementação, sem datas, com checklist e definition of done por fase.
