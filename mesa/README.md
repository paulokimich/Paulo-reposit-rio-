# Mesa de Operações do Paulo

Equipe de agentes que acompanha ações da B3, euro/dólar e oportunidades — no modelo "a mesa analisa, o Paulo assina".

```
              ┌────────────────────┐
              │   CHEFE DA MESA    │  coordena e entrega a ficha
              └─────────┬──────────┘
   ┌──────────┬─────────┼──────────┬──────────────┐
TENDÊNCIA   ESPIÃO   VIGIA CÂMBIO  CAIXA/RENDA   GESTOR DE RISCO
aposta na   segue    euro e dólar  ganha no      decide rápido,
direção     quem tem               fluxo         pode vetar
            vantagem
                                   ▼
                    script `cotacoes.py` puxa os números
                    PAULO ASSINA (executa na corretora dele)
```

## Como usar

1. Edite `mesa/carteira.json` com as ações que você tem/acompanha e os preços de alerta.
2. No seu computador (com Python 3): `python3 mesa/cotacoes.py` — mostra câmbio, ações, tendência e alertas, e salva em `mesa/relatorios/`.
3. Numa sessão do Claude Code neste repositório, peça por exemplo:
   - "Chefe da mesa, como está a PETR4 e vale comprar?"
   - "Vigia do câmbio, é hora de comprar euro?"
   - "Gestor de risco, quero colocar R$ 500 em VALE3."

> Observação: no ambiente de nuvem do Claude, o acesso às APIs de cotação pode estar bloqueado pela rede; nesse caso os agentes pesquisam na web.

## Ficha de Decisão (modelo)

| Campo | Preencher |
|---|---|
| Ativo | |
| Tese em 1 frase | |
| Tendência (Tendência) | alta / baixa / lateral |
| O que os informados fazem (Espião) | |
| Preço de entrada | |
| Stop (onde a tese morre) | |
| Alvo | |
| Tamanho (Gestor de Risco) | qtd e R$ |
| Perda máxima em R$ | |
| Veredito do Gestor de Risco | Aprovado / Menor / Vetado |
| **Assinatura do Paulo** | ☐ Executo ☐ Não executo |

## Regras da mesa

- Reserva de emergência vem antes de qualquer ação.
- Máx. 2% do patrimônio em risco por operação; máx. 20% numa ação só.
- Proibido: alavancagem, day trade, "sinais" pagos, promessas de lucro garantido.
- Perdeu 6% no mês → a mesa para até o mês seguinte.
- Isto é ferramenta de análise, não recomendação de investimento profissional.
