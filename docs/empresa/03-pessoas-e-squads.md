# Pessoas e squads

A lista completa de funcionários, cargos, gestores e squads está no banco, no schema `rh` (ver [banco de dados](../dados/banco-de-dados.md)). Este documento apresenta a liderança e os principais stakeholders do programa Benefy AI SDLC.

## Organograma

```
CEO: Marina Okada
├── CTO: Rafael Duarte
│   ├── Head de Engenharia: Paulo Sampaio
│   │   ├── 4 Engineering Managers
│   │   ├── 2 Arquitetos de Software
│   │   └── 8 squads de produto e plataforma
│   ├── AI Orchestrator: Débora Lins
│   │   └── Squad Plataforma de IA
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

## Squad Plataforma de IA

### Débora Lins: AI Orchestrator
- Lidera o programa Benefy AI SDLC desde mar/2026.
- **Prioridades:** ganhos mensuráveis de produtividade e qualidade.
- **Pontos de atenção:** toda proposta precisa de métrica de sucesso e plano de rollout.

### André Matsuda: AI Engineer Sênior
- Na Benefy desde 2024. Atuou no squad de Autorização e conhece o core do produto.
- Responsável técnico do squad: distribui as demandas, revisa os PRs e define os padrões de implementação.
- **Forma de trabalho:** as demandas chegam com contexto e critério de sucesso. O desenho da solução é discutido antes da implementação.

## Stakeholders

### Rafael Duarte: CTO
- Cofundador.
- **Prioridades:** dobrar a produtividade da engenharia até o fim de 2027.
- **Pontos de atenção:** a pressão por velocidade não dispensa os controles de mudança (quality gate, CAB).

### Paulo Sampaio: Head de Engenharia
- **Prioridades:** padrão único para todos os squads, com espaço para ajustes locais.

### Carla Nunes: CISO
- Dona das regras do SonarQube e do Veracode.
- **Prioridades:** nenhum agente com permissão de escrita em `main`, execução auditável e nenhum segredo saindo do ambiente.
- **Pontos de atenção:** restringiu o uso de IA após o INC-2025-031. Novas iniciativas precisam apresentar controles verificáveis.

### Otávio Reis: DPO
- **Prioridades:** nenhum CPF, nome ou dado de transação de colaborador enviado a modelo de IA externo sem base legal e mascaramento.

### Bianca Teixeira: Product Owner do squad Carteira & Saldo
- Referência em regras de negócio do produto.
- **Prioridades:** estorno parcial e fallback estáveis antes da Black Friday.
- **Pontos de atenção:** algumas histórias chegam sem critério de aceite completo. Ajustes devem ser alinhados com ela no refinamento.

### Lucas Ferreira: Tech Lead do squad Carteira & Saldo
- Desenvolvedor Python sênior, 8 anos de casa.
- **Prioridades:** menos tempo em code review e testes que detectem regressões reais.
- **Pontos de atenção:** tem ressalvas com código gerado por IA, por histórico de regressões no extrato.

### Ana Beatriz Costa: Tech Lead do squad Cartões
- Squad em Java/Spring Boot. Usa Copilot.
- **Prioridades:** ferramentas de IA com suporte a Java.

### Helena Prado: CFO
- **Prioridades:** visibilidade do custo de IA por mês e por squad.

### Patrícia Lopes: Head de Atendimento e CS
- **Prioridades:** menos tickets repetidos e respostas mais rápidas. O atendimento é a primeira área a sentir falhas do produto.

### Marcos Vieira: Gerente Comercial
- Abre itens no Boards quando um cliente estratégico solicita mudanças.

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
| Plataforma de IA | Python | em implantação | 3 |

## Cerimônias

- Sprints de 2 semanas, começando na quarta-feira.
- Daily às 9h30 (15 minutos).
- Refinamento na segunda-feira da segunda semana.
- Review e retro na terça-feira de fim de sprint.
- Change Advisory Board (CAB) para mudanças em produção que afetam autorização: quinta-feira.
- 1:1 com a liderança a cada 2 semanas.
