# Segurança e compliance

## Classificação de dados

| Classe | Exemplos | Pode ir para um modelo de IA externo? |
|---|---|---|
| **Restrito** | CPF, nome completo, número do cartão (PAN), CVV, dados bancários, segredos e chaves | Nunca. Mascarar antes. CVV e PAN nem mascarados. |
| **Confidencial** | Saldo e transações de um colaborador identificável, contratos de clientes | Só anonimizado ou agregado |
| **Interno** | Código-fonte, histórias do backlog, documentação técnica | Sim, em ferramentas aprovadas pela Segurança |
| **Público** | Site, termos de uso | Sim |

## Incidente INC-2025-031

**O que aconteceu (mar/2025):** um dev, investigando um bug no extrato, colou num chatbot de IA público um trecho de log com 214 linhas de transações. As linhas tinham CPF e nome dos colaboradores. O fato só foi descoberto duas semanas depois, numa revisão de rotina.

**Consequências:**
- Comunicação ao DPO e avaliação de risco de notificação à ANPD.
- A CISO proibiu o uso de qualquer ferramenta de IA até existir uma política.
- Em jun/2025 o uso voltou, liberado só para Claude Code e GitHub Copilot em contas corporativas, mas **sem padrão de configuração, sem log e sem controle do que é enviado**.

**Causa raiz:** não havia mascaramento de dados pessoais nos logs nem regra clara sobre o que pode ir para IA.

**Por que isso importa para você:** a Plataforma de IA só vai ser liberada para todos os squads se a Carla (CISO) e o Otávio (DPO) aprovarem os controles. Pense nisso em qualquer código que você escrever (ex: nunca logar CPF).

O banco de homologação usa dados sintéticos, mas a regra é tratar como se fossem reais: CPF, nome e telefone continuam sendo dados **Restritos**.

## Política de uso de IA (versão atual, provisória)

1. Só ferramentas aprovadas: Claude Code e GitHub Copilot, em contas corporativas.
2. Proibido enviar dados das classes Restrito e Confidencial.
3. Código gerado por IA passa pelo mesmo code review e quality gate que qualquer código.
4. Agentes automatizados (sem humano no loop) estão **proibidos** até a nova política ser aprovada.

> O item 4 é o que o programa Benefy AI SDLC precisa mudar, com segurança.

## Requisitos regulatórios e normativos relevantes

| Referência | O que pede (resumo) |
|---|---|
| LGPD (Lei 13.709/2018) | Base legal para tratar dado pessoal, minimização, registro das operações, segurança |
| Lei 14.442/2022 | Uso do VR/VA só para alimentação; proíbe deságio e rebates |
| PCI DSS | Proteção de dados de cartão (PAN, CVV) |
| ISO/IEC 27001 | Gestão de segurança da informação (a Benefy é certificada) |
| ISO/IEC 42001 | Gestão de sistemas de IA (a Benefy quer se certificar em 2027) |
| OWASP Top 10 for LLM Applications | Riscos de aplicações com LLM (prompt injection, vazamento de dados etc.) |

## Controles que a auditoria interna já testa

- Segregação de funções: quem escreve o código não aprova o próprio PR.
- Gestão de mudanças: toda mudança em produção tem PR aprovado, pipeline verde e, para autorização, aprovação do CAB.
- Gestão de acessos: revisão trimestral de quem tem acesso a produção.
- Logs: logs de produção guardados por 5 anos, sem dado pessoal em claro.
