# Robô de Avisos de Vencimento — envio automático pelo WhatsApp

O robô manda **sozinho**, toda manhã (seg–sáb, a partir das 8h de Cuiabá), um aviso
gentil para cada cliente no momento certo. Ninguém precisa clicar.

| Quando | Modelo | Tom |
|---|---|---|
| 3 dias antes de vencer | `aviso_vencimento` | "Passando só para avisar que vence em..." |
| No dia | `aviso_vence_hoje` | "Lembrete rápido: vence hoje..." |
| 1 e 7 dias depois | `aviso_pagamento_pendente` | "Pode ter sido só um esquecimento, acontece..." |
| 15+ dias | — | O robô para. Uma pessoa liga. |

Proteções: nunca manda a mesma mensagem 2x, não manda domingo nem fora do horário,
não manda para quem já pagou, máximo 50 por dia, e começa em **modo teste**
(mostra o que mandaria sem mandar) até o Paulo mandar ligar.

## Por que precisa do WhatsApp oficial

Para a empresa mandar mensagem automática **sem o cliente ter escrito antes**, a única forma
permitida é a API oficial do WhatsApp (Meta). Robô "pirata" em WhatsApp comum leva bloqueio
do número. Na oficial, cada aviso custa uns **R$ 0,05** (categoria Utilidade).
200 avisos/mês ≈ R$ 10.

## Passo a passo (quem faz: seu sogro, com o CNPJ; ~1 hora + espera da Meta)

1. Entrar em **business.facebook.com** e criar o **Portfólio empresarial** da empresa (nome, CNPJ, site ou Instagram).
2. Em **developers.facebook.com** > Meus apps > Criar app > tipo **Empresa** > adicionar o produto **WhatsApp**.
3. **Número:** usar um número que NÃO esteja ativo no WhatsApp comum (chip novo, ~R$ 20).
   Se quiserem usar o número atual do WhatsApp Business, existe a "coexistência" (o app continua funcionando),
   mas depende do provedor; vemos isso juntos.
4. Cadastrar uma **forma de pagamento** na conta do WhatsApp (cartão da empresa).
5. Em WhatsApp > **Modelos de mensagem**, criar os 3 modelos abaixo (categoria **Utilidade**, idioma **Português (BR)**). A Meta costuma aprovar em minutos ou horas.
6. Me passar o **ID do número de telefone** (Phone number ID — não é segredo).
7. Gerar um **token permanente** (usuário do sistema). **NÃO colar no chat**: eu abro um formulário seguro.
8. Eu faço 1 envio de teste para o celular do Paulo e, com o OK dele, ligo o modo automático.

## Os 3 modelos (copiar exatamente)

Variáveis: {{1}} nome do cliente · {{2}} valor · {{3}} nome da empresa · {{4}} data · {{5}} como pagar.
Exemplos para a Meta: {{1}} João · {{2}} R$ 450,00 · {{3}} Loja Exemplo · {{4}} 12/11/2026 · {{5}} escolha Pix ou boleto e responda esta mensagem que a gente envia na hora.

**Nome:** `aviso_vencimento`
> Olá, {{1}}! Tudo bem? 😊 Passando só para avisar que sua parcela de {{2}} com a {{3}} vence em {{4}}. Para pagar: {{5}}. Se já pagou, pode desconsiderar. Qualquer dúvida, é só responder aqui.

**Nome:** `aviso_vence_hoje`
> Olá, {{1}}! Bom dia! Lembrete rápido: sua parcela de {{2}} com a {{3}} vence hoje, {{4}}. Para pagar: {{5}}. Se já pagou, desconsidere. Obrigado pela parceria!

**Nome:** `aviso_pagamento_pendente`
> Olá, {{1}}, tudo bem? Ainda não localizamos o pagamento da parcela de {{2}} com a {{3}}, que venceu em {{4}}. Pode ter sido só um esquecimento, acontece. Para pagar: {{5}}. Se já pagou, desconsidere. Se precisar de outra data, responda aqui que a gente combina. 🙂

## Enquanto a Meta não libera

O robô continua montando a lista toda manhã com o botão "abrir WhatsApp" para alguém enviar
na mão. Mesmo texto, mesma hora. Quando a API ficar pronta, só troca a chave para automático.
