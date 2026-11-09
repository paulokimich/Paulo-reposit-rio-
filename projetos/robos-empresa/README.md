# Robôs da empresa do sogro (via API da Moveri)

Ajuda familiar, sem cobrança. Objetivo: cobrar melhor, organizar o financeiro e atender mais rápido.

## Status

| Robô | Fase | Situação |
|---|---|---|
| Avisos de Vencimento (envio automático) | 1 | **Pronto com dados de exemplo, em modo teste.** Falta: dados reais + WhatsApp oficial (ver MODELOS-WHATSAPP.md) |
| Gerente / Resumo financeiro | 1 | **Pronto (só contas a receber).** Cresce quando a API mostrar caixa e contas a pagar |
| Contábil (fechamento do mês, contas a pagar, pacote do contador) | 1 | **Pronto com extrato de exemplo.** Falta o extrato real do banco (CSV) |
| Pós-venda (lembrete de troca/recapagem) | 1 | A fazer, depende da API (histórico de vendas) |
| Vendedor do WhatsApp — versão grátis | 0 | **Pronto para colar hoje** no app WhatsApp Business: `vendedor/whatsapp-business-hoje.md` |
| Vendedor do WhatsApp com IA (24h) | 2 | **Cérebro pronto** (`vendedor/vendedor.py`). Falta a ficha real da empresa, chave da API do Claude e a conta Meta Business |

O que falta do Paulo: ver [CHECKLIST-paulo.md](CHECKLIST-paulo.md).

## Como funciona (fase 1)

1. `robos/moveri.py` busca as contas a receber (hoje: arquivo de exemplo; depois: API).
2. `robos/cobranca.py` aplica a régua e gera `saida/cobranca-AAAA-MM-DD.md` com mensagem pronta e link do WhatsApp para cada cliente. Uma pessoa clica e envia: custo zero.
3. `robos/resumo.py` gera o resumo do dia para o dono.
4. Quando estiver ligado na API, uma rotina agendada roda os dois toda manhã (seg–sáb) e manda o resultado.

```bash
python3 robos/contabil.py 2026-11 2026-11-09
python3 robos/cobranca.py 2026-11-09
python3 robos/resumo.py 2026-11-09
python3 -m unittest discover -s testes
```

## Regras fixas

- Mensagem de cobrança educada, horário comercial, só para o próprio cliente, sem ameaça nem exposição (CDC art. 42).
- Dados de clientes ficam fora do repositório: `config.json` e `saida/` estão no `.gitignore`. Chave da API nunca no código nem no chat.
- 15+ dias de atraso: quem conversa é uma pessoa, não o robô.

## Custos

- Fase 1: R$ 0–50/mês (rotinas no plano do Claude; envio manual pelo WhatsApp).
- Fase 2: R$ 200–450/mês (servidor, IA, WhatsApp oficial). Pago pela empresa.
