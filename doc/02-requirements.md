# 02 — Requirements

## Índice

- [Convenções](#convenções)
- [Módulo: Autenticação (AUTH)](#módulo-autenticação-auth)
- [Módulo: Usuários e Papéis (USERS)](#módulo-usuários-e-papéis-users)
- [Módulo: Catálogo (CATALOG)](#módulo-catálogo-catalog)
- [Módulo: Estoque (STOCK)](#módulo-estoque-stock)
- [Módulo: Carrinho (CART)](#módulo-carrinho-cart)
- [Módulo: Pedidos (ORDERS)](#módulo-pedidos-orders)
- [Módulo: Checkout (CHECKOUT)](#módulo-checkout-checkout)
- [Módulo: Auditoria (AUDIT)](#módulo-auditoria-audit)
- [Transversal: Cache (CACHE)](#transversal-cache-cache)
- [Transversal: Processamento Assíncrono (ASYNC)](#transversal-processamento-assíncrono-async)
- [Requisitos Não Funcionais (NFR)](#requisitos-não-funcionais-nfr)

---

## Convenções

Cada requisito tem um ID no formato `RF-<MÓDULO>-<NÚMERO>` (requisito funcional) ou `NFR-<NÚMERO>` (não funcional).

Os módulos abaixo correspondem 1:1 às pastas do projeto, seguindo **Package by Feature**: cada módulo (`users/`, `products/`, `cart/`, `orders/`...) contém suas próprias sub-camadas (router, service, repository, schema). Isso significa que este documento pode ser lido módulo por módulo, na mesma ordem em que o código vai ser organizado — não há necessidade de pular entre seções para entender uma funcionalidade completa.

Para cada requisito funcional constam:

- **Descrição** — o que é.
- **Regra de negócio** — a lógica que precisa ser respeitada.
- **Critérios de aceite** — checklist objetivo para saber quando está pronto.
- **Dependências** — o que precisa existir antes.

> **Observação sobre papéis (RBAC):** o sistema usa dois papéis obrigatórios — `admin` e `customer`. Um papel adicional, `staff`, é opcional e só deve ser implementado se, durante o desenvolvimento, fizer sentido separar "quem cadastra produto" de "quem administra o sistema como um todo". Até lá, todo requisito abaixo assume apenas `admin` e `customer`.

---

## Módulo: Autenticação (AUTH)

### RF-AUTH-01 — Registro de usuário

- **Descrição:** permitir que um visitante crie uma conta com e-mail e senha.
- **Regra de negócio:** e-mail deve ser único; senha deve ser armazenada com hash (bcrypt ou argon2, ver NFR); todo usuário criado por este endpoint recebe o papel `customer` por padrão — não é possível se auto-cadastrar como `admin`.
- **Critérios de aceite:**
  - [ ] Cadastro rejeita e-mail duplicado com erro claro.
  - [ ] Senha nunca é retornada em nenhuma resposta, nem em log.
  - [ ] Usuário criado consegue autenticar imediatamente após o cadastro.
- **Dependências:** nenhuma.

### RF-AUTH-02 — Login (emissão de token)

- **Descrição:** autenticar usuário via e-mail/senha e devolver um JWT.
- **Regra de negócio:** usa o esquema OAuth2 Password Flow apenas como padrão de recebimento de credenciais (`OAuth2PasswordBearer`) — não há autorização de terceiros envolvida. O token deve carregar o `id` do usuário e o(s) papel(is), com tempo de expiração definido.
- **Critérios de aceite:**
  - [ ] Credenciais inválidas retornam erro genérico (não revelar se o e-mail existe ou não).
  - [ ] Token expira no tempo configurado.
  - [ ] Payload do token não contém dado sensível (senha, hash etc.).
- **Dependências:** RF-AUTH-01.

### RF-AUTH-03 — Logout / invalidação de token

- **Descrição:** permitir invalidar um token antes do seu tempo natural de expiração.
- **Regra de negócio:** o token invalidado entra em uma blacklist no Redis com TTL igual ao tempo restante de validade do token — evita crescer a blacklist indefinidamente.
- **Critérios de aceite:**
  - [ ] Requisição com token na blacklist é rejeitada mesmo que o token ainda não tenha expirado.
  - [ ] Entrada da blacklist expira sozinha no Redis (sem necessidade de limpeza manual).
- **Dependências:** RF-AUTH-02, Redis configurado.

### RF-AUTH-04 — Autorização por papel (RBAC)

- **Descrição:** restringir endpoints por papel do usuário autenticado.
- **Regra de negócio:** cada endpoint declara explicitamente quais papéis podem acessá-lo. Ausência de papel compatível retorna erro de permissão (não erro de autenticação).
- **Critérios de aceite:**
  - [ ] Endpoint de `admin` retorna erro de permissão para usuário `customer` autenticado.
  - [ ] Erro de "sem permissão" é distinguível de "não autenticado" no formato de resposta (ver NFR de padrão de erro).
- **Dependências:** RF-AUTH-02.

---

## Módulo: Usuários e Papéis (USERS)

### RF-USERS-01 — Consulta do próprio perfil

- **Descrição:** usuário autenticado consulta seus próprios dados.
- **Regra de negócio:** um usuário só pode ver o próprio perfil, exceto `admin`, que pode consultar qualquer perfil.
- **Critérios de aceite:**
  - [ ] `customer` recebe erro de permissão ao tentar acessar perfil de outro usuário.
  - [ ] `admin` consegue consultar qualquer perfil por ID.
- **Dependências:** RF-AUTH-04.

### RF-USERS-02 — Atualização de perfil

- **Descrição:** usuário atualiza seus próprios dados (nome, e-mail, senha).
- **Regra de negócio:** troca de e-mail exige unicidade (mesma regra do cadastro); troca de senha invalida os tokens emitidos anteriormente (força novo login).
- **Critérios de aceite:**
  - [ ] Atualização de senha adiciona os tokens antigos à blacklist ou reduz seu tempo de vida.
  - [ ] Tentativa de trocar para e-mail já existente é rejeitada.
- **Dependências:** RF-AUTH-01, RF-AUTH-03.

### RF-USERS-03 — Gestão de papéis (admin)

- **Descrição:** `admin` promove ou rebaixa o papel de um usuário.
- **Regra de negócio:** um `admin` não pode remover o próprio papel de admin caso seja o único administrador do sistema (evita lockout).
- **Critérios de aceite:**
  - [ ] Sistema rejeita a remoção do último `admin` existente.
  - [ ] Mudança de papel reflete imediatamente nas próximas requisições autenticadas (não exige novo login, já que a checagem de papel pode ser feita no banco, não apenas no token — deixar essa decisão explícita em `03-architecture.md`).
- **Dependências:** RF-AUTH-04.

---

## Módulo: Catálogo (CATALOG)

### RF-CATALOG-01 — Cadastro de categoria

- **Descrição:** `admin` cria categorias de produto.
- **Regra de negócio:** nome de categoria é único; categoria pode ser desativada (soft delete) mas não excluída se houver produtos vinculados.
- **Critérios de aceite:**
  - [ ] Categoria duplicada é rejeitada.
  - [ ] Categoria com produtos vinculados não pode ser removida, apenas desativada.
- **Dependências:** RF-AUTH-04.

### RF-CATALOG-02 — Cadastro de produto

- **Descrição:** `admin` cria produtos vinculados a uma categoria.
- **Regra de negócio:** produto sempre pertence a exatamente uma categoria; preço não pode ser negativo ou zero; produto criado começa com estoque zerado (estoque é ajustado separadamente, ver módulo STOCK).
- **Critérios de aceite:**
  - [ ] Produto sem categoria válida é rejeitado.
  - [ ] Produto com preço ≤ 0 é rejeitado.
- **Dependências:** RF-CATALOG-01.

### RF-CATALOG-03 — Listagem de produtos (com cache)

- **Descrição:** qualquer usuário (autenticado ou não) lista produtos disponíveis, com paginação e filtro por categoria.
- **Regra de negócio:** resultado é cacheado no Redis por um período curto (ex: 60s); apenas produtos ativos e com estoque > 0 aparecem por padrão, com opção de incluir indisponíveis via parâmetro explícito.
- **Critérios de aceite:**
  - [ ] Segunda requisição idêntica é servida do cache (verificável por header ou log).
  - [ ] Alteração de produto invalida o cache da listagem correspondente.
- **Dependências:** RF-CATALOG-02, Redis configurado.

### RF-CATALOG-04 — Detalhe do produto (com cache)

- **Descrição:** consulta de um produto específico por ID.
- **Regra de negócio:** cache individual por produto, invalidado especificamente quando aquele produto é alterado (não a listagem inteira).
- **Critérios de aceite:**
  - [ ] Cache de detalhe é invalidado apenas para o produto alterado, sem afetar cache de outros produtos.
- **Dependências:** RF-CATALOG-02, Redis configurado.

---

## Módulo: Estoque (STOCK)

### RF-STOCK-01 — Ajuste de estoque (admin)

- **Descrição:** `admin` incrementa ou decrementa o estoque de um produto.
- **Regra de negócio:** estoque nunca pode ficar negativo; toda alteração de estoque gera um registro de auditoria (ver módulo AUDIT).
- **Critérios de aceite:**
  - [ ] Tentativa de deixar estoque negativo é rejeitada.
  - [ ] Toda alteração gera entrada de auditoria com motivo (ex: "reposição", "correção manual").
- **Dependências:** RF-CATALOG-02, RF-AUDIT-01.

### RF-STOCK-02 — Reserva de estoque no pedido

- **Descrição:** ao confirmar um pedido, o estoque dos produtos envolvidos é debitado.
- **Regra de negócio:** debitar estoque e criar o pedido deve ser uma operação atômica (mesma transação de banco) — não pode existir pedido confirmado com estoque não debitado, nem debitar estoque sem pedido criado.
- **Critérios de aceite:**
  - [ ] Falha em qualquer etapa reverte a transação inteira (nem pedido nem débito de estoque são persistidos).
  - [ ] Pedido com produto sem estoque suficiente é rejeitado antes da criação.
- **Dependências:** RF-CATALOG-02, RF-ORDERS-01.

---

## Módulo: Carrinho (CART)

### RF-CART-01 — Adicionar item ao carrinho

- **Descrição:** usuário autenticado adiciona produto e quantidade ao próprio carrinho.
- **Regra de negócio:** carrinho é único por usuário (não há múltiplos carrinhos simultâneos); adicionar produto já existente no carrinho soma a quantidade, não duplica a linha.
- **Critérios de aceite:**
  - [ ] Adicionar o mesmo produto duas vezes resulta em uma única linha com quantidade somada.
  - [ ] Quantidade não pode ser adicionada além do estoque disponível.
- **Dependências:** RF-AUTH-04, RF-CATALOG-02.

### RF-CART-02 — Remover ou atualizar item do carrinho

- **Descrição:** usuário altera a quantidade ou remove um item do próprio carrinho.
- **Regra de negócio:** quantidade zero remove o item automaticamente.
- **Critérios de aceite:**
  - [ ] Atualizar quantidade para 0 remove a linha do carrinho.
- **Dependências:** RF-CART-01.

### RF-CART-03 — Consultar carrinho

- **Descrição:** usuário visualiza o próprio carrinho com subtotal calculado.
- **Regra de negócio:** subtotal é sempre calculado no momento da consulta (preço não é "congelado" no carrinho, apenas no pedido após checkout).
- **Critérios de aceite:**
  - [ ] Alteração de preço de um produto reflete no subtotal do carrinho na próxima consulta.
- **Dependências:** RF-CART-01.

---

## Módulo: Pedidos (ORDERS)

### RF-ORDERS-01 — Criação de pedido a partir do carrinho

- **Descrição:** transformar o carrinho atual em um pedido.
- **Regra de negócio:** preço de cada item é "congelado" no momento da criação do pedido (mudanças futuras no catálogo não afetam pedidos já criados); carrinho é esvaziado após a criação bem-sucedida.
- **Critérios de aceite:**
  - [ ] Pedido mantém o preço do momento da compra mesmo que o produto mude de preço depois.
  - [ ] Carrinho fica vazio após pedido criado com sucesso.
- **Dependências:** RF-CART-03, RF-STOCK-02.

### RF-ORDERS-02 — Acompanhamento de status do pedido

- **Descrição:** usuário consulta o status atual de um pedido próprio; `admin` pode consultar qualquer pedido.
- **Regra de negócio:** status segue uma máquina de estados fixa (ver diagrama em `03-architecture.md`): `criado → pagamento_pendente → pago → enviado → concluído`, com `cancelado` como estado alternativo a partir de `criado` ou `pagamento_pendente`.
- **Critérios de aceite:**
  - [ ] Transição de status fora da máquina de estados definida é rejeitada (ex: não é possível ir de `criado` direto para `enviado`).
- **Dependências:** RF-ORDERS-01.

---

## Módulo: Checkout (CHECKOUT)

### RF-CHECKOUT-01 — Processar pagamento simulado

- **Descrição:** simular a aprovação ou recusa de pagamento de um pedido.
- **Regra de negócio:** não há gateway real. O resultado é decidido de forma determinística e simples (ex: parâmetro de teste ou regra simulada), retornando um dos estados: `aprovado` ou `recusado`. Pedido aprovado avança para `pago`; pedido recusado avança para `cancelado`.
- **Critérios de aceite:**
  - [ ] Pagamento aprovado altera o status do pedido para `pago`.
  - [ ] Pagamento recusado altera o status do pedido para `cancelado` e não debita estoque adicional (estoque já foi debitado na criação do pedido — avaliar em `03-architecture.md` se o débito deve ser revertido em caso de recusa).
- **Dependências:** RF-ORDERS-01, RF-ORDERS-02.

---

## Módulo: Auditoria (AUDIT)

### RF-AUDIT-01 — Registro de ações sensíveis

- **Descrição:** registrar quem fez o quê e quando, para ações administrativas e de mudança de estado (ajuste de estoque, mudança de papel, mudança de status de pedido).
- **Regra de negócio:** o registro de auditoria é gravado de forma assíncrona (via Celery) para não impactar o tempo de resposta da ação principal.
- **Critérios de aceite:**
  - [ ] Toda ação sensível listada gera uma entrada de auditoria com: usuário responsável, ação, entidade afetada, timestamp.
  - [ ] Falha na gravação da auditoria não impede a ação principal de ser concluída (é um efeito colateral, não uma dependência bloqueante).
- **Dependências:** RabbitMQ + Celery configurados.

---

## Transversal: Cache (CACHE)

Não é um módulo de negócio, mas uma responsabilidade que atravessa outros módulos (principalmente CATALOG). Está descrita aqui para não ser esquecida na hora de implementar cada requisito que a cita.

- Cache de listagem e detalhe de produto (ver RF-CATALOG-03 e RF-CATALOG-04).
- Rate limiting por IP/usuário nos endpoints públicos (ver NFR-04).
- Blacklist de tokens JWT invalidados (ver RF-AUTH-03).

---

## Transversal: Processamento Assíncrono (ASYNC)

Mesma lógica do Cache: não é um módulo isolado, é uma responsabilidade usada por outros módulos.

- Envio de e-mail (ex: confirmação de pedido) — disparado após RF-ORDERS-01.
- Gravação de auditoria (RF-AUDIT-01).
- Geração de relatórios sob demanda — dois relatórios mínimos: **vendas por período** e **produtos mais vendidos**, gerados de forma assíncrona e consultáveis depois de prontos (não é streaming em tempo real).
- Invalidação de cache quando a alteração de dado é custosa de processar de forma síncrona.

---

## Requisitos Não Funcionais (NFR)

| ID | Requisito | Detalhe |
|---|---|---|
| NFR-01 | Versionamento de API | Todas as rotas expostas sob `/api/v1/...`. |
| NFR-02 | Paginação padrão | Listagens usam `limit`/`offset`, com `limit` default e máximo definidos em `03-architecture.md`. |
| NFR-03 | Formato único de erro | Toda resposta de erro segue uma estrutura padrão (código, mensagem, detalhes), documentada em `05-api-design.md`. |
| NFR-04 | Rate limiting | Limite de requisições por IP/usuário em endpoints públicos, via Redis. |
| NFR-05 | Health check | Endpoints `/health` (liveness) e `/ready` (readiness, checando conexão com MySQL/Redis/RabbitMQ). |
| NFR-06 | Logging estruturado | Logs em formato JSON, com identificador de requisição para correlação. |
| NFR-07 | Hash de senha | bcrypt ou argon2 — escolha e justificativa registradas em `03-architecture.md`. |
| NFR-08 | CORS | Política básica definida mesmo sem frontend fixo. |
| NFR-09 | Dados de demonstração | Script de seed com usuários, papéis, categorias e produtos de exemplo, para permitir teste imediato do sistema. |

---

**Próximo documento:** `03-architecture.md` — como Package by Feature, Ports & Adapters, autenticação, autorização, cache, mensageria e os demais requisitos acima se conectam na prática.
