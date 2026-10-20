# Onboarding: squad Plataforma de IA

Guia da primeira semana para novos integrantes do squad Plataforma de IA.

| Papel | Pessoa |
|---|---|
| Liderança do squad | Débora Lins (AI Orchestrator) |
| Responsável técnico | André Matsuda (AI Engineer Sênior) |

## Fluxo de trabalho

1. A demanda chega pelo Boards ou pelo canal do squad, com contexto e critério de sucesso.
2. O desenho da solução é discutido com o responsável técnico antes da implementação. Dúvidas de negócio vão para o PO do squad dono da regra.
3. A implementação acontece numa branch `feature/BNF-xxx-descricao`, seguindo os [padrões de engenharia](../empresa/05-padroes-de-engenharia.md).
4. O PR é aberto contra a `develop` e passa por revisão humana e pelo quality gate.
5. Depois da aprovação, o merge é feito e o item é fechado no Boards.

Demandas do squad podem envolver serviços, análises de dados, automações, agentes de IA, pipelines e relatórios para outras áreas.

## Checklist da primeira semana

- [ ] Ler a documentação em [docs/empresa](../empresa)
- [ ] Ler o [manual do colaborador](../rh/manual-do-colaborador.md)
- [ ] Concluir o treinamento obrigatório de LGPD e segurança
- [ ] Configurar o git com nome e e-mail corporativos
- [ ] Subir o banco de homologação ([instruções](../dados/banco-de-dados.md)) e executar as consultas de exemplo
- [ ] Alinhar a primeira demanda com o responsável técnico

## Acessos

| Ferramenta | Situação |
|---|---|
| Repositório central | Concedido no primeiro dia |
| Banco de homologação | PostgreSQL local em Docker, porta 5433 |
| Claude Code | Conta corporativa |
| AWS | Conta de sandbox, solicitada ao responsável técnico conforme a demanda |
| Azure DevOps | Solicitado ao responsável técnico conforme a demanda |
| Produção | Sem acesso para o squad |
