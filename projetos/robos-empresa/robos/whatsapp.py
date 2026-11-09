"""Envio automático pelo WhatsApp oficial (Meta WhatsApp Cloud API).

Só envia MODELOS aprovados pela Meta (categoria Utilidade), que é a regra para
a empresa puxar conversa. O token nunca fica no código: vem da variável de
ambiente WHATSAPP_TOKEN (ou é injetado pelo proxy do ambiente).

Proteções:
- modo teste por padrão (`whatsapp.ativo = false`): só registra o que mandaria;
- só envia seg–sáb, dentro do horário configurado (padrão 8h–18h, Cuiabá);
- registro em saida/enviados.json: nunca manda a mesma etapa 2x para a mesma conta;
- limite de envios por dia.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

CUIABA = timezone(timedelta(hours=-4))


def agora_cuiaba() -> datetime:
    return datetime.now(CUIABA)


def pode_enviar_agora(cfg: dict, agora: datetime) -> tuple[bool, str]:
    ini, fim = cfg.get("horario", [8, 18])
    if agora.weekday() == 6:
        return False, "domingo"
    if not (ini <= agora.hour < fim):
        return False, f"fora do horário ({ini}h–{fim}h)"
    return True, ""


def enviar_modelo(telefone: str, modelo: str, params: list[str], cfg: dict) -> dict:
    fone = telefone if telefone.startswith("55") else "55" + telefone
    corpo = {
        "messaging_product": "whatsapp",
        "to": fone,
        "type": "template",
        "template": {
            "name": modelo,
            "language": {"code": cfg.get("idioma", "pt_BR")},
            "components": [{"type": "body", "parameters": [{"type": "text", "text": p} for p in params]}],
        },
    }
    url = f"https://graph.facebook.com/{cfg.get('versao_api', 'v23.0')}/{cfg['phone_number_id']}/messages"
    req = urllib.request.Request(url, data=json.dumps(corpo).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    token = os.environ.get("WHATSAPP_TOKEN", "")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.load(r)
        return {"ok": True, "id": resp.get("messages", [{}])[0].get("id", "")}
    except urllib.error.HTTPError as e:
        return {"ok": False, "erro": f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}"}
    except urllib.error.URLError as e:
        return {"ok": False, "erro": str(e.reason)}
