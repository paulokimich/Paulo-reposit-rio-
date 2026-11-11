# O que o Paulo precisa trazer

Marque com [x] conforme for conseguindo. Pode trazer aos poucos.

## Meta: primeira cobrança real na quarta, 11/11, às 7h

Prazo para trazer: **terça, 10/11, até o meio-dia.**

- [ ] **Plano B (garante a quarta mesmo se a Moveri atrasar):** uma **planilha de contas a receber** exportada do sistema (Excel ou CSV) com cliente, telefone, valor, vencimento e se foi pago. Pode mandar pra mim pelo chat do Claude, ela NÃO vai pro repositório.

## Agora (destrava o robô de cobrança com dados reais)

- [ ] **Documentação da API da Moveri** (link ou PDF). Perguntar:
  - Qual o endereço da API (URL base)?
  - Como autentica (token/chave no cabeçalho? qual cabeçalho?)
  - Tem rota de **contas a receber / boletos / títulos**? Traz telefone do cliente?
  - Tem ambiente de teste (sandbox)?
  - A API só **lê** ou também **altera/envia** algo?
  - Tem limite de chamadas por dia?
- [ ] **Chave da API** — NÃO colar no chat. Quando tiver, me avise que eu abro um formulário seguro.
- [ ] **Nome da empresa** como deve aparecer na assinatura das mensagens.
- [x] **Como o cliente paga:** ele escolhe Pix ou boleto. Falta: a chave Pix da empresa (e, se a Moveri tiver, o link do boleto de cada parcela).
- [x] **Quem envia** nas primeiras semanas: a moça da cobrança (uma só, para as 22 lojas). Falta: onde ela quer receber a lista toda manhã.
- [ ] **Régua de cobrança** que o seu sogro aceita (atual: lembrete 3 dias antes e no dia; carência de 10 dias por causa da baixa; aviso com 11 e 18 dias de atraso; com 25+ dias uma pessoa liga).

## Robô de Pós-venda

- [ ] **Histórico de vendas** dos últimos 6 meses (planilha): cliente, telefone, o que comprou e data. Coluna opcional `nao_contatar` para quem não quer receber mensagem.

## Robô Contábil

- [ ] **Extrato do banco do mês** exportado do internet banking (CSV ou Excel). Se tiver mais de um banco, um de cada.
- [ ] **Contas a pagar** do mês (planilha ou lista: o quê, valor, vencimento).

## Robô Vendedor do WhatsApp

- [ ] **Hoje, grátis:** colar as mensagens de `vendedor/whatsapp-business-hoje.md` no WhatsApp Business da empresa (30 min).
- [ ] **Ficha da empresa** preenchida (o modelo é `vendedor/empresa.example.json`): o que vende, os 20 produtos mais vendidos com preço, endereço, horário, entrega, pagamento, quem é o vendedor humano. Pode mandar em texto ou foto da tabela que eu monto.

## Depois (resumo financeiro completo)

- [ ] A API mostra **caixa do dia, contas a pagar e vendas**?
- [ ] E-mail ou WhatsApp do seu sogro e do **contador** para receber o resumo.

## Fase 2 (robô que responde mensagens 24h)

- [ ] Conta **Meta Business** da empresa (quem cria é o dono, com CNPJ).
- [ ] Um **número de WhatsApp** só para o robô (chip novo, ~R$ 20).
- [ ] Lista das **10 perguntas que os clientes mais fazem** e as respostas certas.
