"""Robô Vendedor do WhatsApp (fase 2).

Recebe a mensagem do cliente, responde como um vendedor da loja usando SÓ o que
está na ficha da empresa (`empresa.json`), qualifica o pedido e passa para um
vendedor humano quando precisa (desconto, frota, reclamação, algo fora da ficha).

Esta é a parte "cérebro". A ligação com o WhatsApp oficial (Meta Cloud API) e o
servidor entram quando a empresa tiver a conta Meta Business.

Testar no terminal (precisa de ANTHROPIC_API_KEY):
    python3 vendedor/vendedor.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

PASTA = Path(__file__).resolve().parent
MODELO_PADRAO = "claude-opus-5-5"  # pode trocar para "claude-haiku-5-5" em config para custar ~20x menos
SINAL_HUMANO = "[PASSAR_PARA_HUMANO]"

MANUAL = """Você é o atendente virtual da {nome}, uma loja em Cuiabá/MT. Você conversa pelo WhatsApp com clientes.

Seu trabalho: responder rápido, ajudar o cliente a escolher, passar o preço e levar até o pedido. Fale como um bom vendedor de Cuiabá: educado, direto, simpático, frases curtas, sem textão. No máximo 3 frases curtas por mensagem, salvo quando listar opções. Use o nome do cliente se ele disser. Pode usar no máximo 1 emoji por mensagem.

Regras fixas:
1. Só informe preço, prazo, estoque, garantia ou condição que estejam na FICHA abaixo. Se não estiver na ficha, diga que vai confirmar com o vendedor e passe para humano. Nunca invente.
2. Para pneu, pergunte a medida (está escrita na lateral, ex.: 175/70 R13) ou o modelo do carro/caminhão e o ano.
3. Quando o cliente quiser fechar, colete: nome, medida/produto, quantidade, forma de pagamento, retirar ou entregar (com endereço). Depois faça um resumo do pedido e passe para humano para confirmar.
4. Passe para humano quando: pedido de desconto, frota ou empresa com 3+ veículos, reclamação, garantia em análise, cliente irritado, cliente pedir pessoa, ou qualquer dúvida fora da ficha.
5. Para passar para humano, termine sua mensagem com uma frase avisando que um vendedor vai continuar e coloque na ÚLTIMA linha exatamente: {sinal}
6. Nunca peça senha, dados de cartão ou documentos. Pagamento só pelos meios da ficha.
7. Se perguntarem se é robô, diga que é o atendente virtual da loja e que um vendedor pode assumir quando quiser.
8. Fora do horário da loja, responda normalmente e avise que a confirmação do pedido sai no próximo horário de atendimento.

FICHA DA EMPRESA (única fonte de verdade):
{ficha}
"""


def carregar_ficha() -> dict:
    caminho = PASTA / "empresa.json"
    if not caminho.exists():
        caminho = PASTA / "empresa.example.json"
    return json.loads(caminho.read_text(encoding="utf-8"))


def montar_sistema(ficha: dict) -> str:
    dados = {k: v for k, v in ficha.items() if not k.startswith("_")}
    # JSON com chaves ordenadas: o texto não muda entre mensagens, então o cache funciona.
    return MANUAL.format(nome=ficha["nome"], sinal=SINAL_HUMANO,
                         ficha=json.dumps(dados, ensure_ascii=False, indent=1, sort_keys=True))


def separar_resposta(texto: str) -> tuple[str, bool]:
    """Tira o sinal de humano do texto que vai para o cliente."""
    humano = SINAL_HUMANO in texto
    limpo = re.sub(re.escape(SINAL_HUMANO), "", texto).strip()
    return limpo, humano


def responder(historico: list[dict], ficha: dict, modelo: str = MODELO_PADRAO, cliente=None) -> tuple[str, bool]:
    """historico = [{"role": "user"|"assistant", "content": "..."}]. Devolve (texto, passar_para_humano)."""
    import anthropic

    cliente = cliente or anthropic.Anthropic()
    extra = {"betas": ["server-side-fallback-2026-07-01"], "fallbacks": "default"} if modelo != "claude-haiku-5-5" else {}
    criar = cliente.beta.messages.create if extra else cliente.messages.create
    resp = criar(
        model=modelo,
        max_tokens=1024,
        system=montar_sistema(ficha),
        cache_control={"type": "ephemeral"},
        output_config={"effort": "low"},
        messages=historico,
        **extra,
    )
    if resp.stop_reason == "refusal":
        return "Vou chamar um vendedor para te atender, só um instante.", True
    texto = "".join(b.text for b in resp.content if b.type == "text")
    return separar_resposta(texto)


def main() -> None:
    ficha = carregar_ficha()
    historico: list[dict] = []
    print(f"Simulador do vendedor da {ficha['nome']}. Escreva como cliente (sair = Ctrl+C).\n")
    while True:
        historico.append({"role": "user", "content": input("Cliente: ")})
        texto, humano = responder(historico, ficha)
        historico.append({"role": "assistant", "content": texto})
        print(f"Robô: {texto}" + ("\n   >>> passou para o vendedor humano" if humano else "") + "\n")


if __name__ == "__main__":
    main()
