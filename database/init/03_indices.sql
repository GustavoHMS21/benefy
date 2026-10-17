CREATE INDEX idx_transacoes_colaborador_data ON beneficios.transacoes (colaborador_id, data_hora);
CREATE INDEX idx_transacoes_data ON beneficios.transacoes (data_hora);
CREATE INDEX idx_colaboradores_empresa ON beneficios.colaboradores (empresa_id);
CREATE INDEX idx_cartoes_colaborador ON beneficios.cartoes (colaborador_id);
CREATE INDEX idx_tickets_colaborador ON atendimento.tickets (colaborador_id);
CREATE INDEX idx_funcionarios_departamento ON rh.funcionarios (departamento_id);

ANALYZE;
