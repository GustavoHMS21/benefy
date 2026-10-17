-- Gerado por tools/seed/gerar_seed.py. Não edite à mão.
\set ON_ERROR_STOP on
BEGIN;
\copy rh.departamentos (id, nome, centro_custo, gestor_id) FROM '/seed/rh.departamentos.csv' WITH (FORMAT csv, HEADER true)
\copy rh.cargos (id, titulo, trilha, nivel, faixa_min_centavos, faixa_max_centavos) FROM '/seed/rh.cargos.csv' WITH (FORMAT csv, HEADER true)
\copy rh.funcionarios (id, matricula, nome, email, cpf, data_nascimento, data_admissao, data_desligamento, departamento_id, cargo_id, gestor_id, salario_base_centavos, modelo_trabalho, cidade, uf, status) FROM '/seed/rh.funcionarios.csv' WITH (FORMAT csv, HEADER true)
\copy rh.squads (id, nome, slug, linguagem_principal, tech_lead_id, product_owner_id, engineering_manager_id) FROM '/seed/rh.squads.csv' WITH (FORMAT csv, HEADER true)
\copy rh.squad_membros (squad_id, funcionario_id, papel) FROM '/seed/rh.squad_membros.csv' WITH (FORMAT csv, HEADER true)
\copy rh.ferias (id, funcionario_id, inicio, fim, status) FROM '/seed/rh.ferias.csv' WITH (FORMAT csv, HEADER true)
\copy rh.avaliacoes_desempenho (id, funcionario_id, ciclo, avaliador_id, nota, comentario) FROM '/seed/rh.avaliacoes_desempenho.csv' WITH (FORMAT csv, HEADER true)
\copy rh.folha_pagamento (id, funcionario_id, competencia, salario_base_centavos, bonus_centavos, beneficios_centavos, encargos_centavos, custo_total_centavos) FROM '/seed/rh.folha_pagamento.csv' WITH (FORMAT csv, HEADER true)
\copy comercial.planos (codigo, nome, mensalidade_por_colaborador_centavos, descricao) FROM '/seed/comercial.planos.csv' WITH (FORMAT csv, HEADER true)
\copy beneficios.tipos_carteira (codigo, nome, descricao) FROM '/seed/beneficios.tipos_carteira.csv' WITH (FORMAT csv, HEADER true)
\copy comercial.empresas_clientes (id, razao_social, cnpj, setor, porte, cidade, uf, plano_codigo, fallback_livre, limite_diario_centavos, status, cliente_desde, executivo_conta_id) FROM '/seed/comercial.empresas_clientes.csv' WITH (FORMAT csv, HEADER true)
\copy comercial.empresa_carteiras (empresa_id, carteira_codigo, habilitada, credito_mensal_padrao_centavos) FROM '/seed/comercial.empresa_carteiras.csv' WITH (FORMAT csv, HEADER true)
\copy beneficios.mcc (codigo, descricao, carteira_codigo, bloqueado) FROM '/seed/beneficios.mcc.csv' WITH (FORMAT csv, HEADER true)
\copy beneficios.estabelecimentos (id, nome, cnpj, mcc, cidade, uf, parceiro) FROM '/seed/beneficios.estabelecimentos.csv' WITH (FORMAT csv, HEADER true)
\copy beneficios.colaboradores (id, empresa_id, nome, cpf, email, telefone, data_nascimento, data_desligamento, status, criado_em) FROM '/seed/beneficios.colaboradores.csv' WITH (FORMAT csv, HEADER true)
\copy beneficios.cartoes (id, colaborador_id, final_cartao, status, emitido_em, validade, bloqueado_em) FROM '/seed/beneficios.cartoes.csv' WITH (FORMAT csv, HEADER true)
\copy beneficios.pedidos_credito (id, empresa_id, competencia, data_credito, status, valor_total_centavos) FROM '/seed/beneficios.pedidos_credito.csv' WITH (FORMAT csv, HEADER true)
\copy beneficios.pedido_credito_itens (pedido_id, colaborador_id, carteira_codigo, valor_centavos) FROM '/seed/beneficios.pedido_credito_itens.csv' WITH (FORMAT csv, HEADER true)
\copy beneficios.transacoes (id, colaborador_id, cartao_id, estabelecimento_id, mcc, valor_centavos, data_hora, status, motivo_negacao) FROM '/seed/beneficios.transacoes.csv' WITH (FORMAT csv, HEADER true)
\copy beneficios.estornos (id, transacao_id, valor_centavos, data_hora, solicitado_por) FROM '/seed/beneficios.estornos.csv' WITH (FORMAT csv, HEADER true)
\copy beneficios.lancamentos (id, colaborador_id, carteira_codigo, tipo, valor_centavos, origem_tipo, origem_id, data_hora) FROM '/seed/beneficios.lancamentos.csv' WITH (FORMAT csv, HEADER true)
\copy beneficios.carteiras (colaborador_id, carteira_codigo, saldo_centavos, atualizado_em) FROM '/seed/beneficios.carteiras.csv' WITH (FORMAT csv, HEADER true)
\copy financeiro.fornecedores (id, nome, categoria) FROM '/seed/financeiro.fornecedores.csv' WITH (FORMAT csv, HEADER true)
\copy financeiro.despesas (id, fornecedor_id, centro_custo, competencia, valor_centavos, descricao) FROM '/seed/financeiro.despesas.csv' WITH (FORMAT csv, HEADER true)
\copy financeiro.faturas (id, empresa_id, competencia, valor_creditos_centavos, valor_mensalidade_centavos, valor_total_centavos, vencimento, status, pago_em) FROM '/seed/financeiro.faturas.csv' WITH (FORMAT csv, HEADER true)
\copy atendimento.tickets (id, aberto_em, canal, solicitante_tipo, colaborador_id, empresa_id, categoria, prioridade, status, assunto, descricao, atendente_id, resolvido_em, nota_satisfacao) FROM '/seed/atendimento.tickets.csv' WITH (FORMAT csv, HEADER true)
\copy engenharia.servicos (nome, squad_id, linguagem, repositorio, criticidade, situacao, descricao) FROM '/seed/engenharia.servicos.csv' WITH (FORMAT csv, HEADER true)
\copy engenharia.work_items (id, tipo, squad_slug, titulo, descricao, criterios_aceite, estado, autor_id, responsavel_id, criado_em) FROM '/seed/engenharia.work_items.csv' WITH (FORMAT csv, HEADER true)
\copy engenharia.incidentes (id, titulo, severidade, servico, inicio, fim, status, resumo, causa_raiz) FROM '/seed/engenharia.incidentes.csv' WITH (FORMAT csv, HEADER true)
UPDATE rh.departamentos SET gestor_id = 1 WHERE id = 1;
UPDATE rh.departamentos SET gestor_id = 2 WHERE id = 2;
UPDATE rh.departamentos SET gestor_id = 122 WHERE id = 3;
UPDATE rh.departamentos SET gestor_id = 15 WHERE id = 4;
UPDATE rh.departamentos SET gestor_id = 137 WHERE id = 5;
UPDATE rh.departamentos SET gestor_id = 4 WHERE id = 6;
UPDATE rh.departamentos SET gestor_id = 3 WHERE id = 7;
UPDATE rh.departamentos SET gestor_id = 166 WHERE id = 8;
UPDATE rh.departamentos SET gestor_id = 220 WHERE id = 9;
UPDATE rh.departamentos SET gestor_id = 316 WHERE id = 10;
UPDATE rh.departamentos SET gestor_id = 338 WHERE id = 11;
UPDATE rh.departamentos SET gestor_id = 350 WHERE id = 12;
UPDATE rh.departamentos SET gestor_id = 368 WHERE id = 13;
COMMIT;
