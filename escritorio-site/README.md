# Paulo Office — escritório com mesas

## Entrega atual

Site estático de arquivo único (`index.html`), sem dependências ou serviços externos. Tela responsiva, seis especialistas em suas mesas, mesa do gerente e mesa de Paulo. Personagens e mesas são desenhados em CSS; as imagens da referência não são utilizadas como ativos.

Fluxo implementado e validado em navegador: criar tarefa → escrever relatório → especialista entrega ao gerente com animação → preencher parecer do gerente → encaminhar para Paulo com animação → aprovar ou solicitar ajustes → retornar ao especialista. As etapas e textos são manuais, sem chamadas a modelos de IA. Os dados permanecem no localStorage do mesmo navegador e origem; o botão de exportação gera um resumo em Markdown. Não há sincronização entre dispositivos, autenticação, corretora ou integração com o painel de pneus.

## Publicação estática

- Diretório de publicação: pasta contendo `index.html`.
- Comando de build: nenhum; não é um projeto Node.
- Dependências de execução: nenhuma.
- Publicar apenas o arquivo `index.html` na raiz do diretório público. Os arquivos Markdown e capturas não são necessários.
- Usar uma hospedagem com HTTPS e endereço estável. Não tratar uma URL local ou um arquivo do ambiente de desenvolvimento como site público.
- A verificação da publicação deve incluir acesso ao endereço HTTPS externo e o fluxo em navegador móvel. O teste local não comprova publicação.

## Limitação de publicação nesta sessão

Não há ferramenta de hospedagem conectada. A consulta de leitura à API do GitHub com a configuração existente retornou `Forbidden`. Isso não estabelece que o token seja inválido: pode haver restrição de rede ou de escopo. Não extrair o valor do token nem substituir autenticação. Credenciais da Vercel, Netlify e Cloudflare não estão presentes. Nenhuma publicação foi realizada.

Falta escolher e conectar uma hospedagem pelo método suportado, ou transferir o arquivo para publicação manual pelo proprietário. Não solicitar senha ou token pelo chat. Domínio próprio é opcional; o endereço padrão gratuito da hospedagem é suficiente para a primeira versão.

## Evolução para agentes conectados

Pesquisa automática, uso de modelos e revisão por IA precisam de um serviço no servidor, armazenamento persistente e autenticação. Chaves não devem ficar no HTML nem no localStorage. A interface deve refletir tarefas reais de uma fila e resultados de execução; não usar timers para fingir pesquisa ou inventar relatórios. O gerente e o proprietário precisam de caixas de entrada distintas. Aprovação de tarefa não equivale a autorização para executar ordens financeiras ou enviar mensagens.

## Validação executada

Teste automatizado em Chromium: fluxo completo com ciclo de ajuste, aprovação, recarga e persistência, exportação com conteúdo desta execução, layouts de 360, 390, 768 e 1440 pixels, ausência de transbordamento horizontal e de erros JavaScript. Dados de teste removidos. Nenhum dado de negócio real foi inserido.
