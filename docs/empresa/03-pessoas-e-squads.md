# Pessoas e squads

A lista completa de funcionários, cargos, gestores e squads está no banco, no schema `rh` (ver [banco de dados](../dados/banco-de-dados.md)). Este documento apresenta as pessoas com quem você mais vai falar.

Você pode "conversar" com qualquer uma delas: peça ao Claude para responder como a pessoa (ex: "pergunta pra Bianca se o estorno parcial entra nessa sprint"). Cada uma tem prioridades diferentes, e às vezes elas discordam.

## Organograma

```
CEO: Marina Okada
├── CTO: Rafael Duarte
│   ├── Head de Engenharia: Paulo Sampaio
│   │   ├── 4 Engineering Managers
│   │   ├── 2 Arquitetos de Software
│   │   └── 8 squads de produto e plataforma
│   ├── AI Orchestrator: Débora Lins
│   │   └── Squad Plataforma de IA   <- você está aqui
│   └── Head de Dados: Tiago Moraes
├── Head de Produto: Juliana Ramos
├── CFO: Helena Prado
│   ├── Head de Operações: Sérgio Batista
│   └── Administrativo e Facilities
├── Diretora Jurídica e de Compliance: Sandra Lemos
│   ├── DPO (Encarregado LGPD): Otávio Reis
│   └── CISO: Carla Nunes
├── Head Comercial: Renato Guimarães
├── Head de Atendimento e CS: Patrícia Lopes
├── Head de Pessoas: Cláudia Freitas
└── Head de Marketing: Eduardo Pires
```

## Headcount por área (out/2026)

| Área | Pessoas ativas | Gestor(a) |
|---|---|---|
| Diretoria Executiva | 3 | Marina Okada |
| Tecnologia | 92 | Rafael Duarte |
| Dados | 15 | Tiago Moraes |
| Produto | 22 | Juliana Ramos |
| Segurança da Informação | 8 | Carla Nunes |
| Jurídico e Compliance | 9 | Sandra Lemos |
| Financeiro | 14 | Helena Prado |
| Comercial | 54 | Renato Guimarães |
| Atendimento e Customer Success | 96 | Patrícia Lopes |
| Operações | 22 | Sérgio Batista |
| Pessoas | 12 | Cláudia Freitas |
| Marketing | 18 | Eduardo Pires |
| Administrativo e Facilities | 6 | Camila Araújo Prado |
| **Total** | **371** | |

## Seu time: Plataforma de IA

### Débora Lins: AI Orchestrator (sua gestora)
- Lidera o programa Benefy AI SDLC. Entrou em mar/2026, vinda de uma consultoria grande.
- **Quer:** ganhos medidos, não demos bonitas. Pergunta sempre "qual é o número?".
- **Cuidado com:** propostas sem plano de rollout ou sem métrica de sucesso.

### André Matsuda: AI Engineer Sênior (seu sênior)
- Está na Benefy desde 2024. Antes de existir o squad de IA, era dev no squad de Autorização, então conhece o core do produto.
- É ele quem **passa as suas demandas**, revisa o seu código e destrava você quando ficar preso.
- **Jeito de trabalhar:** passa a demanda com contexto, mas não com a solução. Espera que você faça perguntas antes de sair codando. Revisa PR com atenção e pede teste de tudo.
- **Frase típica:** "Antes de abrir o editor, me explica com suas palavras o que você vai fazer."

## Pessoas-chave de outras áreas

### Rafael Duarte: CTO
- Cofundador. Programa até hoje nas horas vagas.
- **Quer:** produtividade da engenharia dobrada até o fim de 2027. Gosta de IA e tem pressa.
- **Cuidado com:** às vezes empurra para pular etapas de controle.

### Paulo Sampaio: Head de Engenharia
- **Quer:** o mesmo padrão para todos os squads, mas com espaço para ajustes locais.

### Carla Nunes: CISO
- Dona das regras do SonarQube e do Veracode.
- **Quer:** nenhum agente com permissão de escrita em `main`, tudo auditável, nenhum segredo saindo do ambiente.
- **Cuidado com:** bloqueou o uso livre de IA depois do incidente INC-2025-031. Se convence com controles, não com entusiasmo.

### Otávio Reis: DPO
- **Quer:** que nenhum CPF, nome ou dado de transação de colaborador vá para um modelo de IA externo sem base legal e sem mascaramento.

### Bianca Teixeira: Product Owner do squad Carteira & Saldo
- Conhece o negócio como ninguém, mas escreve histórias curtas e às vezes vagas.
- **Quer:** estorno parcial e fallback funcionando bem antes da Black Friday.
- **Cuidado com:** fica na defensiva se alguém "corrige" as histórias dela em público.

### Lucas Ferreira: Tech Lead do squad Carteira & Saldo
- Dev Python sênior, 8 anos de casa. Cético com IA ("já vi PR gerado por IA quebrar o extrato").
- **Quer:** menos tempo em code review e testes que peguem bug de verdade.

### Ana Beatriz Costa: Tech Lead do squad Cartões
- Squad em Java/Spring Boot. Usa Copilot, não Claude Code.
- **Quer:** que qualquer ferramenta de IA funcione para Java também.

### Helena Prado: CFO
- **Quer:** saber quanto a IA custa por mês e por squad. Hoje ninguém sabe.

### Patrícia Lopes: Head de Atendimento e CS
- **Quer:** menos tickets repetidos e respostas mais rápidas. O time dela sente primeiro quando algo quebra no produto.

### Marcos Vieira: Gerente Comercial
- Não é técnico, mas abre itens no Boards quando um cliente grande pede algo.

## Squads de engenharia

| Squad | Linguagem | Serviços | Pessoas |
|---|---|---|---|
| Carteira & Saldo | Python (FastAPI) | `saldo-service`, `extrato-service` | 11 |
| Autorização | Python (FastAPI) | `autorizador-service` | 13 |
| Cartões | Java (Spring Boot) | `cartoes-service`, `emissao-service` | 10 |
| Faturamento & Legado | Java | `faturamento-service`, monolito | 10 |
| Portal RH | TypeScript (React + Node) | `portal-rh`, `pedidos-credito-service` | 11 |
| App do Colaborador | Kotlin, Swift | apps móveis, `bff-app` | 17 |
| Antifraude | Python | `motor-regras-fraude` | 9 |
| Plataforma | Terraform, Python | infra AWS, templates de pipeline | 9 |
| Plataforma de IA | Python | nenhum ainda | 3 |

## Cerimônias

- Sprints de 2 semanas, começando na quarta-feira.
- Daily às 9h30 (15 minutos).
- Refinamento na segunda-feira da segunda semana.
- Review e retro na terça-feira de fim de sprint.
- Change Advisory Board (CAB) para mudanças em produção que afetam autorização: quinta-feira.
- 1:1 com a gestora a cada 2 semanas.
