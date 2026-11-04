# Análise Financeira — Comissão de pneus e projeção de patrimônio em 12 meses

**Data:** 04/11/2026 · **Autor:** Analista Financeiro · **Para:** Paulo (Cuiabá-MT)

> **Aviso importante:** os preços de pneu abaixo são **estimativas de mercado**, não são os preços da loja do Paulo. A taxa Selic/CDI usada é **premissa**, não cotação conferida hoje. Antes de decidir, confira: (1) a tabela de preços da loja, (2) como a comissão aparece no holerite, (3) a Selic atual no site do Banco Central / Tesouro Direto.

---

## 0. Premissas

| Item | Valor usado | Observação |
|---|---|---|
| Renda | R$ 5.500/mês | Não sabemos se é bruto ou líquido; confirmar no holerite |
| Gasto mensal | R$ 1.000/mês | Sobra teórica de R$ 4.500/mês |
| Aporte planejado | R$ 3.000/mês | Deixa R$ 1.500/mês de folga (bom) |
| Comissão pneu novo | "1,2" | Cenário A = 1,2% do valor · Cenário B = R$ 1,20 por pneu |
| Comissão recapado | "2,2" | Cenário A = 2,2% do valor · Cenário B = R$ 2,20 por pneu |
| Pneu de passeio | R$ 350–450 → **média R$ 400** | Estimativa |
| Pneu de caminhonete | R$ 700–1.000 → **média R$ 850** | Estimativa |
| Pneu de caminhão novo | R$ 2.000–2.800 → **média R$ 2.400** | Estimativa |
| Recapagem de caminhão | R$ 600–900 → **média R$ 750** | Estimativa |
| Carteira de ações hoje | R$ 3.201,96 (custo R$ 3.746,40) | Já está -R$ 544,44 (-14,5%) |

**Imposto sobre comissão:** comissão de empregado CLT entra na folha (INSS + IRRF), não é MEI/Simples. Com salário na faixa de R$ 5.500, o desconto marginal sobre cada real extra pode ficar entre **~25% e ~45%** (INSS até 14% + IR marginal, incluindo o efeito da faixa de transição da isenção até R$ 5.000 vigente desde 2026). **Premissa conservadora: o Paulo fica com ~65% do valor bruto da comissão extra.** Conferir com o holerite ou com um contador.

---

## 1. Tabela de comissão por pneu — dois cenários

Fórmulas:
- Cenário A (%): `comissão = preço médio × taxa`
- Cenário B (R$ fixo): `comissão = R$ 1,20 (novo) ou R$ 2,20 (recapado)`, independente do preço

| Produto | Preço médio (estimado) | Cenário A — conta | Cenário A — R$/unid. | Cenário B — R$/unid. |
|---|---|---|---|---|
| Pneu de passeio (novo) | R$ 400 | 400 × 1,2% | **R$ 4,80** | **R$ 1,20** |
| Pneu de caminhonete (novo) | R$ 850 | 850 × 1,2% | **R$ 10,20** | **R$ 1,20** |
| Pneu de caminhão (novo) | R$ 2.400 | 2.400 × 1,2% | **R$ 28,80** | **R$ 1,20** |
| Recapagem de caminhão | R$ 750 | 750 × 2,2% | **R$ 16,50** | **R$ 2,20** |

Leitura rápida:
- No cenário **%**, o pneu de caminhão novo paga **6x** o de passeio. Foco em frota/caminhão.
- No cenário **R$ fixo**, todo pneu novo paga igual: o que importa é **volume**, e recapagem paga quase o dobro.
- No cenário %, a recapagem (R$ 16,50) paga mais que caminhonete e tem venda recorrente para frotas: bom produto para "carteira de clientes".

---

## 2. Vendas extras por mês para +R$ 500 e +R$ 1.000 (bruto)

Fórmula: `vendas extras = meta ÷ comissão por unidade` (arredondado para cima)

| Produto | Cenário A (%) +R$ 500 | Cenário A (%) +R$ 1.000 | Cenário B (R$ fixo) +R$ 500 | Cenário B (R$ fixo) +R$ 1.000 |
|---|---|---|---|---|
| Passeio | 500 ÷ 4,80 = **105** | 1.000 ÷ 4,80 = **209** | 500 ÷ 1,20 = **417** | 1.000 ÷ 1,20 = **834** |
| Caminhonete | 500 ÷ 10,20 = **50** | 1.000 ÷ 10,20 = **99** | 500 ÷ 1,20 = **417** | 1.000 ÷ 1,20 = **834** |
| Caminhão novo | 500 ÷ 28,80 = **18** | 1.000 ÷ 28,80 = **35** | 500 ÷ 1,20 = **417** | 1.000 ÷ 1,20 = **834** |
| Recapagem | 500 ÷ 16,50 = **31** | 1.000 ÷ 16,50 = **61** | 500 ÷ 2,20 = **228** | 1.000 ÷ 2,20 = **455** |

Em dias úteis (≈ 22/mês), por exemplo: 18 pneus de caminhão extras = **menos de 1 por dia útil**; 417 pneus de passeio extras = **19 por dia útil**.

**Líquido (premissa de 65%):** para colocar R$ 500 **no bolso**, a meta bruta vira 500 ÷ 0,65 ≈ **R$ 770**, ou seja, cerca de **54% a mais de vendas** do que a tabela acima.

### Conclusão sobre a comissão

- **Se for R$ fixo por pneu (Cenário B): NÃO é um bom caminho.** 417 a 834 pneus extras/mês não são realistas para um vendedor. O esforço extra rende ~R$ 1,20 por pneu; o tempo do Paulo vale mais em outra frente (serviço próprio/MEI).
- **Se for % do valor (Cenário A): é um caminho bom apenas focado em caminhão e recapagem.** 18 a 35 pneus de caminhão novos extras, ou 31 a 61 recapagens extras/mês, é viável **se** o Paulo prospectar frotas (transportadoras, fazendas, empresas de ônibus em Cuiabá/Várzea Grande). Com passeio, não vale.
- **Primeiro passo obrigatório:** descobrir qual é o cenário. Pegar o último holerite e dividir o valor da comissão pelo total vendido no mês. Se der ~1,2%, é percentual; se der um valor irrisório, é R$ fixo.

---

## 3. Projeção de patrimônio — 12 meses

### Premissas

| Item | Valor | Observação |
|---|---|---|
| Meses 1–2 | R$ 3.000/mês 100% no Tesouro Selic | Montar reserva de R$ 6.000 (6x o gasto mensal: adequado) |
| Meses 3–12 | R$ 3.000/mês: **50% Tesouro Selic / 50% renda variável** | Divisão é premissa; a decisão final é da Mesa/Paulo |
| Carteira inicial de ações | R$ 3.201,96 | Valor de mercado atual |
| Aporte | No fim do mês (não rende no mês do aporte) | Conservador |
| Selic bruta (premissa) | Pessimista 11% a.a. · Realista 13% a.a. · Otimista 13,7% a.a. | **Não conferida hoje**: verificar no site do BCB/Tesouro |
| Selic líquida | bruta × (1 − 22,5% IR) | IR regressivo: 22,5% até 180 dias, 20% até 360 dias; usei 22,5% (pior caso) |
| Taxa mensal RF líquida | Pess. 0,68% · Real. 0,80% · Otim. 0,85% | Ex.: 13% × 0,775 = 10,08% a.a. → (1,1008)^(1/12) − 1 ≈ 0,80% a.m. |
| Renda variável | Pess. **0%** · Real. 0,8% a.m. (~10% a.a.) · Otim. 1,2% a.m. (~15% a.a.) | Ações podem cair: ver teste de estresse abaixo |
| Taxa de custódia Tesouro Selic | R$ 0 | Isenta até R$ 10 mil no Tesouro Selic (conferir regra B3 vigente) |

Fórmula mês a mês:
`RF(m) = RF(m−1) × (1 + taxa RF) + aporte RF`
`RV(m) = RV(m−1) × (1 + taxa RV) + aporte RV`

**Total aportado em 12 meses:** 3.201,96 (carteira atual) + 12 × 3.000 = **R$ 39.201,96**

### Tabela resumida (R$)

| Mês | Aporte acumulado* | Pessimista — RF | Pessimista — RV | **Pessimista — Total** | **Realista — Total** | **Otimista — Total** |
|---|---|---|---|---|---|---|
| 1 | 6.201,96 | 3.000,00 | 3.201,96 | **6.201,96** | 6.227,58 | 6.240,38 |
| 2 | 9.201,96 | 6.020,40 | 3.201,96 | **9.222,36** | 9.277,40 | 9.304,77 |
| 3 | 12.201,96 | 7.561,34 | 4.701,96 | **12.263,30** | 12.351,62 | 12.395,34 |
| 6 | 21.201,96 | 12.247,31 | 9.201,96 | **21.449,27** | 21.722,62 | 21.858,32 |
| 9 | 30.201,96 | 17.029,53 | 13.701,96 | **30.731,49** | 31.320,34 | 31.615,36 |
| 12 | 39.201,96 | 21.909,97 | 18.201,96 | **40.111,93** | 41.150,25 | 41.675,86 |

*Inclui a carteira atual de R$ 3.201,96.

**Rendimento em 12 meses (total − aportado):** Pessimista **+R$ 910** · Realista **+R$ 1.948** · Otimista **+R$ 2.474**.

### Teste de estresse (não é o pessimista oficial, é o "e se der ruim")
Se as ações caírem **20%** no mês 12: RV pessimista 18.201,96 × 0,80 = 14.561,57 → total ≈ **R$ 36.471**, ou seja, **−R$ 2.731 abaixo do aportado**. A reserva de R$ 6.000+ no Tesouro Selic fica intacta. Por isso a reserva vem **antes** das ações.

### Leitura
- **O que faz o patrimônio crescer é o aporte, não o rendimento.** Dos ~R$ 40 mil, ~R$ 39 mil é dinheiro do próprio Paulo. A diferença entre pessimista e otimista é só ~R$ 1.560 em 12 meses.
- Ganhar +R$ 500/mês de renda extra (R$ 6.000/ano) vale mais que **3x** o rendimento realista da carteira inteira no ano. **Foco de energia: renda, não rentabilidade.**
- **Alerta de risco:** a carteira atual já perdeu 14,5%. Nada de colocar em ações dinheiro que o Paulo precise nos próximos 2–3 anos. Não aumentar a fatia de RV antes de a reserva de R$ 6.000 estar completa.
- **Alerta de fluxo:** se os R$ 5.500 forem salário **bruto**, o líquido pode ser ~R$ 4.500–4.700; com gasto de R$ 1.000, o aporte de R$ 3.000 continua viável, mas a folga cai. Conferir no holerite.

---

## Pendências a conferir
1. Holerite: comissão é % ou R$ fixo? Salário de R$ 5.500 é bruto ou líquido?
2. Tabela de preços real da loja (substituir as médias estimadas).
3. Selic atual e taxa do Tesouro Selic no dia (site do Tesouro Direto / Banco Central).
4. Tributação da comissão na folha (INSS/IRRF 2026): com contador ou RH.

**Próximo passo (hoje):** pegar o último holerite, dividir o valor da comissão pelo total vendido no mês e descobrir se a comissão é % (≈1,2%) ou R$ fixo. Isso decide se vale a pena correr atrás de frotas de caminhão.
