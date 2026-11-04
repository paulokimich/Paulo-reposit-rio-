# Paulo Office — site novo com equipe em mesas

## Preferência atual do Paulo

Criar um site novo, independente do painel existente, com tema escuro e robôs coloridos em mesas. Cada especialista entrega papéis ao gerente; o gerente revisa e encaminha para Paulo decidir. Priorizar uso pelo celular. Usar hospedagem gratuita para a primeira versão.

## Responsabilidades

- ChatGPT: gerente e responsável pelo prompt e pela organização das frentes.
- Claude: colaboração nas implementações e tarefas transferidas explicitamente por Paulo; preservar o escritório existente e seus dados.
- Paulo: proprietário e aprovador final. Uma aprovação visual não executa mensagens, pedidos ou ordens de investimento.

## Mesas e trabalho

Comercial: pneus e cotações com dados confirmados. Oportunidades: pesquisa e prospecção com fontes. Criação & sites: ofertas digitais (cinco artes e tabela digital por R$ 150, uma rodada de ajustes, sem bio; site à parte). Mercado: pesquisa de investimentos. Risco: revisão de hipóteses e exposição. Caixa: custos e recebimentos separados de patrimônio pessoal.

O gerente deve organizar prioridades, verificar evidências, apontar pendências e encaminhar um parecer claro com a próxima ação. Nenhuma análise, preço, contato ou resultado financeiro deve ser inventado.

## Implementação atual

`escritorio-site/index.html`: site independente, sem build, com interface para mesas, tarefas, relatórios, pareceres, animação de transporte de papéis, pedido de ajustes e aprovação. Testado em Chromium e em larguras de 360 a 1440 pixels. Dados manuais salvos somente no navegador; exportação em Markdown. Sem integrações com serviços de IA ou com o painel existente. Esta versão não representa agentes executando pesquisas automaticamente.

`netlify.toml`: publica exclusivamente a pasta `escritorio-site`. Ao importar no Netlify, selecionar a branch `codex/paulo-office-mesas`. O proprietário precisa criar a conta gratuita e conectar o repositório. Publicação e endereço HTTPS ainda pendentes; validar o endereço externo depois do deploy.

## Próxima evolução

Conectar tarefas a uma fila e serviço de IA real com armazenamento no servidor e autenticação. A animação deve refletir o estado confirmado dos trabalhos, sem simulação de pesquisas. Segredos ficam somente no servidor. ChatGPT e Claude não compartilham memória automaticamente: usar exportações ou uma integração autenticada e verificada.
