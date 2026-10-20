# Produtos e regras de negócio

Fonte da verdade das regras de negócio do produto. Os testes BDD, as histórias do backlog e os agentes de IA usam este documento como referência.

> Resumo operacional das regras, alinhado ao PAT (Programa de Alimentação do Trabalhador) e à Lei 14.442/2022. Não substitui o parecer do Jurídico.

## 1. Conceitos

- **Empresa cliente:** quem contrata a Benefy (ex: Grupo Varella).
- **Colaborador:** funcionário da empresa cliente que recebe o cartão.
- **Carteira:** um "bolso" de saldo dentro da conta do colaborador. Cada carteira só aceita certos tipos de estabelecimento.
- **Estabelecimento:** loja onde o cartão é usado. Cada estabelecimento tem um **MCC** (Merchant Category Code), um código de 4 dígitos que diz o ramo dele.
- **Autorização:** a decisão de aprovar ou negar uma compra, tomada em tempo real.

## 2. Carteiras

| Carteira | Código | Para que serve | MCCs aceitos |
|---|---|---|---|
| Refeição (VR) | `REFEICAO` | Refeições prontas | 5812, 5814 |
| Alimentação (VA) | `ALIMENTACAO` | Compras de mercado | 5411, 5422, 5441, 5451, 5462, 5499 |
| Mobilidade | `MOBILIDADE` | Transporte e combustível | 4111, 4121, 4131, 5541, 5542 |
| Saúde | `SAUDE` | Farmácia e saúde | 5912, 8011, 8021, 8099 |
| Cultura | `CULTURA` | Livros, cinema, shows | 5942, 7832, 7922 |
| Saldo Livre | `LIVRE` | Uso livre | Qualquer MCC, exceto os bloqueados (seção 4) |

**Referência de MCCs**

| MCC | Ramo |
|---|---|
| 4111 | Transporte urbano (metrô, trem) |
| 4121 | Táxi e aplicativos de transporte |
| 4131 | Ônibus |
| 5411 | Supermercados |
| 5422 | Açougues |
| 5441 | Docerias |
| 5451 | Laticínios |
| 5462 | Padarias |
| 5499 | Mercearias e lojas de conveniência de alimentos |
| 5541 | Postos de combustível |
| 5542 | Bombas de combustível automáticas |
| 5812 | Restaurantes |
| 5814 | Fast food e lanchonetes |
| 5912 | Farmácias |
| 5942 | Livrarias |
| 7832 | Cinemas |
| 7922 | Teatros e shows |
| 7995 | Apostas e jogos de azar |
| 8011 | Médicos |
| 8021 | Dentistas |
| 8099 | Outros serviços de saúde |

## 3. Regras de autorização

Uma compra chega com: `colaborador_id`, `valor`, `mcc`, `estabelecimento_id`, `data_hora`. A ordem de verificação é esta:

| # | Regra | Resultado se falhar |
|---|---|---|
| R1 | O colaborador existe e o cartão está **ativo** | Negada: `CARTAO_INATIVO` |
| R2 | O valor é maior que zero e tem no máximo 2 casas decimais | Negada: `VALOR_INVALIDO` |
| R3 | O MCC não está na lista de bloqueio global | Negada: `MCC_BLOQUEADO` |
| R4 | Existe carteira compatível com o MCC e **habilitada** pela empresa cliente | Negada: `SEM_CARTEIRA_COMPATIVEL` |
| R5 | A carteira compatível tem saldo suficiente (ver fallback) | Negada: `SALDO_INSUFICIENTE` |
| R6 | A compra não ultrapassa o limite diário do colaborador | Negada: `LIMITE_DIARIO_EXCEDIDO` |

Se tudo passar: **aprovada**, o saldo é debitado e a transação é registrada.

### 3.1 Escolha da carteira

- Se o MCC é aceito por uma carteira específica (VR, VA, Mobilidade, Saúde, Cultura), o débito sai **dessa carteira**.
- Se o MCC só é aceito pelo Saldo Livre, o débito sai do Saldo Livre.
- Um MCC nunca pertence a mais de uma carteira específica.
- Se a carteira específica do MCC estiver **desabilitada** pela empresa cliente, a compra é negada com `SEM_CARTEIRA_COMPATIVEL`, mesmo havendo saldo no Livre. A empresa desabilitou aquele tipo de gasto de propósito.
- Se o MCC só é aceito pelo Saldo Livre e o Livre está desabilitado, a compra também é negada com `SEM_CARTEIRA_COMPATIVEL`.

### 3.2 Fallback para Saldo Livre

A empresa cliente pode ligar o **fallback** (`fallback_livre = true`). Com ele ligado:

- Se a carteira específica não tem saldo suficiente, o **restante** sai do Saldo Livre.
- Exemplo: compra de R$ 50 no mercado, VA com R$ 30, Livre com R$ 100. Resultado: debita R$ 30 do VA e R$ 20 do Livre. Aprovada.
- Se a soma das duas carteiras não cobre o valor, a compra é **negada inteira** (`SALDO_INSUFICIENTE`). Nada é debitado.
- O fallback **nunca** acontece no sentido contrário (Livre não puxa de VA/VR).
- **Exceção legal:** o saldo de VR e VA não pode ser usado fora de alimentação. Por isso o fallback só vai do específico **para** o Livre, nunca usa VR/VA em outro ramo.

### 3.3 Limite diário

- Padrão: R$ 1.500,00 por colaborador por dia, somando todas as carteiras.
- A empresa cliente pode configurar outro valor, entre R$ 100,00 e R$ 5.000,00.
- O dia é o dia calendário no fuso de São Paulo (`America/Sao_Paulo`).

### 3.4 Estorno

- Uma transação aprovada pode ser estornada em até 30 dias.
- O valor volta para as **mesmas carteiras** de onde saiu, na mesma proporção.
- Estorno parcial é permitido. Um estorno não pode ultrapassar o valor ainda não estornado.
- **Divisão proporcional:** para cada carteira, a parte devolvida é `valor_estorno * debito_da_carteira / valor_total`, arredondada para baixo em centavos. Os centavos que sobrarem do arredondamento voltam para a carteira específica (nunca para o Livre).
- Motivos de recusa do estorno: `ESTORNO_EXCEDE_VALOR` (passou do valor restante) e `ESTORNO_FORA_DO_PRAZO` (mais de 30 dias).

## 4. Bloqueios globais

MCCs bloqueados em **todas** as carteiras, inclusive no Saldo Livre:

| MCC | Motivo |
|---|---|
| 7995 | Apostas e jogos de azar (política da Benefy) |

## 5. Créditos

- A empresa cliente faz um **pedido de crédito** informando colaborador, carteira e valor.
- Os créditos caem no dia 1 de cada mês, ou na data que a empresa escolher.
- O saldo é cumulativo: o que não foi gasto continua na carteira.
- O valor mínimo de crédito por carteira é R$ 1,00.

## 6. Desligamento do colaborador

- Quando a empresa desliga um colaborador, o cartão continua ativo por **90 dias** para ele gastar o saldo restante.
- Nesse período a empresa não pode fazer novos créditos para ele.
- Depois de 90 dias o cartão é cancelado. O saldo que sobrar segue o contrato com a empresa cliente (tratado pelo Jurídico e pelo Comercial, fora do escopo deste documento).

## 7. Dinheiro no código

- Todo valor monetário é armazenado em **centavos, como inteiro** (R$ 12,34 vira `1234`). Nunca use `float` para dinheiro.
- Toda alteração de saldo gera um lançamento no **extrato** (débito ou crédito, com carteira, valor, data e origem). O saldo de uma carteira deve ser sempre igual à soma dos lançamentos dela.
