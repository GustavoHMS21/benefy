# Operação de atendimento

Responsável: Patrícia Lopes (Head de Atendimento e CS). 96 pessoas, em dois turnos (7h às 15h e 14h às 22h).

## Canais

| Canal | Quem usa | Horário |
|---|---|---|
| App (chat dentro do app) | Colaboradores | 7h às 22h |
| Chat no site | Colaboradores e estabelecimentos | 7h às 22h |
| Telefone | Todos | 8h às 20h |
| E-mail | Empresas clientes e estabelecimentos | Resposta em horário comercial |

## Categorias de ticket

| Categoria | Exemplo |
|---|---|
| COMPRA_NEGADA | "Minha compra foi recusada e eu tinha saldo" |
| SALDO_DIVERGENTE | "O saldo não bate com o extrato" |
| CARTAO_BLOQUEADO | "Meu cartão foi bloqueado" |
| SEGUNDA_VIA | "Perdi meu cartão" |
| ESTORNO | "Cancelei a compra e quero o dinheiro de volta" |
| DUVIDA_CARTEIRA | "Posso usar o VR no mercado?" |
| APP_ERRO | "O app fecha sozinho" |
| PEDIDO_CREDITO | Empresa: "O pedido do mês está pendente" |
| FATURA | Empresa: "Preciso da segunda via do boleto" |
| CADASTRO_COLABORADOR | Empresa: "Preciso incluir colaboradores" |
| RELATORIO | Empresa: "Preciso do relatório de uso" |
| CREDENCIAMENTO | Estabelecimento: "Quero aceitar Benefy" |
| REPASSE | Estabelecimento: "O repasse não caiu" |

## SLA de resolução

| Prioridade | Prazo |
|---|---|
| CRITICA | 4 horas |
| ALTA | 24 horas |
| MEDIA | 48 horas |
| BAIXA | 72 horas |

## Ciclo do ticket

`ABERTO` (ninguém pegou) → `EM_ANDAMENTO` (com atendente) → `RESOLVIDO` (resposta dada) → `FECHADO` (cliente confirmou ou passaram 3 dias). No fechamento, o cliente pode dar nota de 1 a 5.

## Escalonamento para engenharia

Quando o atendente não consegue resolver (ex: saldo divergente), o supervisor abre um item no Azure Boards para o squad dono do serviço. Hoje isso é manual e demora em média 2 dias.

## Problema conhecido

Os atendentes copiam o texto do cliente para o ticket, e muitos clientes escrevem CPF e telefone na mensagem. Esses tickets ficam guardados com dado pessoal em claro.
