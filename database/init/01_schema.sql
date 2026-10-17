-- Benefy: banco de homologação (cópia sintética da produção)
-- Um schema por área da empresa. Dinheiro sempre em centavos (bigint).

CREATE SCHEMA rh;
CREATE SCHEMA comercial;
CREATE SCHEMA beneficios;
CREATE SCHEMA financeiro;
CREATE SCHEMA atendimento;
CREATE SCHEMA engenharia;

-- =====================================================================
-- RH: a própria Benefy (funcionários, cargos, squads, folha)
-- =====================================================================

CREATE TABLE rh.departamentos (
    id              smallint PRIMARY KEY,
    nome            text NOT NULL UNIQUE,
    centro_custo    text NOT NULL UNIQUE,
    gestor_id       integer            -- FK adicionada depois de rh.funcionarios
);

CREATE TABLE rh.cargos (
    id                  smallint PRIMARY KEY,
    titulo              text NOT NULL UNIQUE,
    trilha              text NOT NULL,
    nivel               text NOT NULL,
    faixa_min_centavos  bigint NOT NULL,
    faixa_max_centavos  bigint NOT NULL,
    CHECK (faixa_min_centavos < faixa_max_centavos)
);

CREATE TABLE rh.funcionarios (
    id                      integer PRIMARY KEY,
    matricula               text NOT NULL UNIQUE,
    nome                    text NOT NULL,
    email                   text NOT NULL UNIQUE,
    cpf                     text NOT NULL,
    data_nascimento         date NOT NULL,
    data_admissao           date NOT NULL,
    data_desligamento       date,
    departamento_id         smallint NOT NULL REFERENCES rh.departamentos(id),
    cargo_id                smallint NOT NULL REFERENCES rh.cargos(id),
    gestor_id               integer REFERENCES rh.funcionarios(id),
    salario_base_centavos   bigint NOT NULL,
    modelo_trabalho         text NOT NULL CHECK (modelo_trabalho IN ('HIBRIDO', 'REMOTO', 'PRESENCIAL')),
    cidade                  text NOT NULL,
    uf                      char(2) NOT NULL,
    status                  text NOT NULL CHECK (status IN ('ATIVO', 'AFASTADO', 'DESLIGADO'))
);

ALTER TABLE rh.departamentos
    ADD CONSTRAINT fk_departamento_gestor FOREIGN KEY (gestor_id) REFERENCES rh.funcionarios(id);

CREATE TABLE rh.squads (
    id                    smallint PRIMARY KEY,
    nome                  text NOT NULL UNIQUE,
    slug                  text NOT NULL UNIQUE,
    linguagem_principal   text NOT NULL,
    tech_lead_id          integer REFERENCES rh.funcionarios(id),
    product_owner_id      integer REFERENCES rh.funcionarios(id),
    engineering_manager_id integer REFERENCES rh.funcionarios(id)
);

CREATE TABLE rh.squad_membros (
    squad_id        smallint NOT NULL REFERENCES rh.squads(id),
    funcionario_id  integer NOT NULL REFERENCES rh.funcionarios(id),
    papel           text NOT NULL,
    PRIMARY KEY (squad_id, funcionario_id)
);

CREATE TABLE rh.ferias (
    id              integer PRIMARY KEY,
    funcionario_id  integer NOT NULL REFERENCES rh.funcionarios(id),
    inicio          date NOT NULL,
    fim             date NOT NULL,
    status          text NOT NULL CHECK (status IN ('PROGRAMADA', 'GOZADA', 'CANCELADA')),
    CHECK (inicio <= fim)
);

CREATE TABLE rh.avaliacoes_desempenho (
    id              integer PRIMARY KEY,
    funcionario_id  integer NOT NULL REFERENCES rh.funcionarios(id),
    ciclo           text NOT NULL,
    avaliador_id    integer REFERENCES rh.funcionarios(id),
    nota            smallint NOT NULL CHECK (nota BETWEEN 1 AND 5),
    comentario      text,
    UNIQUE (funcionario_id, ciclo)
);

CREATE TABLE rh.folha_pagamento (
    id                      integer PRIMARY KEY,
    funcionario_id          integer NOT NULL REFERENCES rh.funcionarios(id),
    competencia             date NOT NULL,
    salario_base_centavos   bigint NOT NULL,
    bonus_centavos          bigint NOT NULL DEFAULT 0,
    beneficios_centavos     bigint NOT NULL,
    encargos_centavos       bigint NOT NULL,
    custo_total_centavos    bigint NOT NULL,
    UNIQUE (funcionario_id, competencia)
);

-- =====================================================================
-- COMERCIAL: empresas clientes e planos
-- =====================================================================

CREATE TABLE comercial.planos (
    codigo                              text PRIMARY KEY,
    nome                                text NOT NULL,
    mensalidade_por_colaborador_centavos bigint NOT NULL,
    descricao                           text NOT NULL
);

CREATE TABLE comercial.empresas_clientes (
    id                      text PRIMARY KEY,
    razao_social            text NOT NULL,
    cnpj                    text NOT NULL UNIQUE,
    setor                   text NOT NULL,
    porte                   text NOT NULL CHECK (porte IN ('PEQUENA', 'MEDIA', 'GRANDE')),
    cidade                  text NOT NULL,
    uf                      char(2) NOT NULL,
    plano_codigo            text NOT NULL REFERENCES comercial.planos(codigo),
    fallback_livre          boolean NOT NULL DEFAULT false,
    limite_diario_centavos  bigint NOT NULL DEFAULT 150000,
    status                  text NOT NULL CHECK (status IN ('ATIVA', 'SUSPENSA', 'CANCELADA')),
    cliente_desde           date NOT NULL,
    executivo_conta_id      integer REFERENCES rh.funcionarios(id)
);

CREATE TABLE comercial.empresa_carteiras (
    empresa_id                  text NOT NULL REFERENCES comercial.empresas_clientes(id),
    carteira_codigo             text NOT NULL,
    habilitada                  boolean NOT NULL,
    credito_mensal_padrao_centavos bigint NOT NULL DEFAULT 0,
    PRIMARY KEY (empresa_id, carteira_codigo)
);

-- =====================================================================
-- BENEFICIOS: o core do produto (colaboradores, cartões, saldo, transações)
-- =====================================================================

CREATE TABLE beneficios.tipos_carteira (
    codigo      text PRIMARY KEY,
    nome        text NOT NULL,
    descricao   text NOT NULL
);

ALTER TABLE comercial.empresa_carteiras
    ADD CONSTRAINT fk_empresa_carteira_tipo FOREIGN KEY (carteira_codigo) REFERENCES beneficios.tipos_carteira(codigo);

CREATE TABLE beneficios.mcc (
    codigo           char(4) PRIMARY KEY,
    descricao        text NOT NULL,
    carteira_codigo  text REFERENCES beneficios.tipos_carteira(codigo),  -- NULL = só Saldo Livre
    bloqueado        boolean NOT NULL DEFAULT false
);

CREATE TABLE beneficios.estabelecimentos (
    id          text PRIMARY KEY,
    nome        text NOT NULL,
    cnpj        text NOT NULL,
    mcc         char(4) NOT NULL REFERENCES beneficios.mcc(codigo),
    cidade      text NOT NULL,
    uf          char(2) NOT NULL,
    parceiro    boolean NOT NULL DEFAULT false
);

CREATE TABLE beneficios.colaboradores (
    id                  text PRIMARY KEY,
    empresa_id          text NOT NULL REFERENCES comercial.empresas_clientes(id),
    nome                text NOT NULL,
    cpf                 text NOT NULL,
    email               text,
    telefone            text,
    data_nascimento     date NOT NULL,
    data_desligamento   date,
    status              text NOT NULL CHECK (status IN ('ATIVO', 'DESLIGADO')),
    criado_em           timestamptz NOT NULL
);

CREATE TABLE beneficios.cartoes (
    id              text PRIMARY KEY,
    colaborador_id  text NOT NULL REFERENCES beneficios.colaboradores(id),
    final_cartao    char(4) NOT NULL,
    status          text NOT NULL CHECK (status IN ('ATIVO', 'BLOQUEADO', 'CANCELADO')),
    emitido_em      date NOT NULL,
    validade        date NOT NULL,
    bloqueado_em    timestamptz
);

CREATE TABLE beneficios.carteiras (
    colaborador_id   text NOT NULL REFERENCES beneficios.colaboradores(id),
    carteira_codigo  text NOT NULL REFERENCES beneficios.tipos_carteira(codigo),
    saldo_centavos   bigint NOT NULL,
    atualizado_em    timestamptz NOT NULL,
    PRIMARY KEY (colaborador_id, carteira_codigo)
);

CREATE TABLE beneficios.pedidos_credito (
    id                   text PRIMARY KEY,
    empresa_id           text NOT NULL REFERENCES comercial.empresas_clientes(id),
    competencia          date NOT NULL,
    data_credito         date NOT NULL,
    status               text NOT NULL CHECK (status IN ('PENDENTE', 'CREDITADO', 'CANCELADO')),
    valor_total_centavos bigint NOT NULL,
    UNIQUE (empresa_id, competencia)
);

CREATE TABLE beneficios.pedido_credito_itens (
    pedido_id        text NOT NULL REFERENCES beneficios.pedidos_credito(id),
    colaborador_id   text NOT NULL REFERENCES beneficios.colaboradores(id),
    carteira_codigo  text NOT NULL REFERENCES beneficios.tipos_carteira(codigo),
    valor_centavos   bigint NOT NULL CHECK (valor_centavos >= 100),
    PRIMARY KEY (pedido_id, colaborador_id, carteira_codigo)
);

CREATE TABLE beneficios.transacoes (
    id                  text PRIMARY KEY,
    colaborador_id      text NOT NULL REFERENCES beneficios.colaboradores(id),
    cartao_id           text NOT NULL REFERENCES beneficios.cartoes(id),
    estabelecimento_id  text NOT NULL REFERENCES beneficios.estabelecimentos(id),
    mcc                 char(4) NOT NULL REFERENCES beneficios.mcc(codigo),
    valor_centavos      bigint NOT NULL,
    data_hora           timestamptz NOT NULL,
    status              text NOT NULL CHECK (status IN ('APROVADA', 'NEGADA')),
    motivo_negacao      text
);

CREATE TABLE beneficios.estornos (
    id              text PRIMARY KEY,
    transacao_id    text NOT NULL REFERENCES beneficios.transacoes(id),
    valor_centavos  bigint NOT NULL,
    data_hora       timestamptz NOT NULL,
    solicitado_por  text NOT NULL
);

CREATE TABLE beneficios.lancamentos (
    id               bigint PRIMARY KEY,
    colaborador_id   text NOT NULL REFERENCES beneficios.colaboradores(id),
    carteira_codigo  text NOT NULL REFERENCES beneficios.tipos_carteira(codigo),
    tipo             text NOT NULL CHECK (tipo IN ('CREDITO', 'DEBITO', 'ESTORNO')),
    valor_centavos   bigint NOT NULL CHECK (valor_centavos > 0),
    origem_tipo      text NOT NULL CHECK (origem_tipo IN ('PEDIDO_CREDITO', 'TRANSACAO', 'ESTORNO')),
    origem_id        text NOT NULL,
    data_hora        timestamptz NOT NULL
);

-- =====================================================================
-- FINANCEIRO: faturas para clientes, despesas com fornecedores
-- =====================================================================

CREATE TABLE financeiro.fornecedores (
    id          smallint PRIMARY KEY,
    nome        text NOT NULL UNIQUE,
    categoria   text NOT NULL
);

CREATE TABLE financeiro.despesas (
    id                  integer PRIMARY KEY,
    fornecedor_id       smallint NOT NULL REFERENCES financeiro.fornecedores(id),
    centro_custo        text NOT NULL,
    competencia         date NOT NULL,
    valor_centavos      bigint NOT NULL,
    descricao           text NOT NULL
);

CREATE TABLE financeiro.faturas (
    id                          text PRIMARY KEY,
    empresa_id                  text NOT NULL REFERENCES comercial.empresas_clientes(id),
    competencia                 date NOT NULL,
    valor_creditos_centavos     bigint NOT NULL,
    valor_mensalidade_centavos  bigint NOT NULL,
    valor_total_centavos        bigint NOT NULL,
    vencimento                  date NOT NULL,
    status                      text NOT NULL CHECK (status IN ('EM_ABERTO', 'PAGA', 'VENCIDA')),
    pago_em                     date,
    UNIQUE (empresa_id, competencia)
);

-- =====================================================================
-- ATENDIMENTO: tickets de colaboradores, empresas e estabelecimentos
-- =====================================================================

CREATE TABLE atendimento.tickets (
    id                  text PRIMARY KEY,
    aberto_em           timestamptz NOT NULL,
    canal               text NOT NULL CHECK (canal IN ('APP', 'CHAT', 'TELEFONE', 'EMAIL')),
    solicitante_tipo    text NOT NULL CHECK (solicitante_tipo IN ('COLABORADOR', 'EMPRESA', 'ESTABELECIMENTO')),
    colaborador_id      text REFERENCES beneficios.colaboradores(id),
    empresa_id          text REFERENCES comercial.empresas_clientes(id),
    categoria           text NOT NULL,
    prioridade          text NOT NULL CHECK (prioridade IN ('BAIXA', 'MEDIA', 'ALTA', 'CRITICA')),
    status              text NOT NULL CHECK (status IN ('ABERTO', 'EM_ANDAMENTO', 'RESOLVIDO', 'FECHADO')),
    assunto             text NOT NULL,
    descricao           text NOT NULL,
    atendente_id        integer REFERENCES rh.funcionarios(id),
    resolvido_em        timestamptz,
    nota_satisfacao     smallint CHECK (nota_satisfacao BETWEEN 1 AND 5)
);

-- =====================================================================
-- ENGENHARIA: serviços, backlog (Azure Boards) e incidentes
-- =====================================================================

CREATE TABLE engenharia.servicos (
    nome            text PRIMARY KEY,
    squad_id        smallint REFERENCES rh.squads(id),
    linguagem       text NOT NULL,
    repositorio     text NOT NULL,
    criticidade     text NOT NULL CHECK (criticidade IN ('BAIXA', 'MEDIA', 'ALTA', 'CRITICA')),
    situacao        text NOT NULL CHECK (situacao IN ('PRODUCAO', 'MIGRANDO', 'LEGADO')),
    descricao       text NOT NULL
);

CREATE TABLE engenharia.work_items (
    id                  text PRIMARY KEY,
    tipo                text NOT NULL CHECK (tipo IN ('HISTORIA', 'BUG', 'TAREFA')),
    squad_slug          text NOT NULL,
    titulo              text NOT NULL,
    descricao           text NOT NULL,
    criterios_aceite    text NOT NULL DEFAULT '',
    estado              text NOT NULL,
    autor_id            integer REFERENCES rh.funcionarios(id),
    responsavel_id      integer REFERENCES rh.funcionarios(id),
    criado_em           timestamptz NOT NULL
);

CREATE TABLE engenharia.incidentes (
    id              text PRIMARY KEY,
    titulo          text NOT NULL,
    severidade      text NOT NULL CHECK (severidade IN ('SEV1', 'SEV2', 'SEV3')),
    servico         text NOT NULL,
    inicio          timestamptz NOT NULL,
    fim             timestamptz,
    status          text NOT NULL CHECK (status IN ('ABERTO', 'EM_INVESTIGACAO', 'RESOLVIDO')),
    resumo          text NOT NULL,
    causa_raiz      text
);
