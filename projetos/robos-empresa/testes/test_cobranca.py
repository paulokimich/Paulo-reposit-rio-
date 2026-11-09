import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "robos"))
from cobranca import brl, lista_do_dia  # noqa: E402
from moveri import carregar_config, contas_a_receber  # noqa: E402
from resumo import resumo  # noqa: E402


class TestCobranca(unittest.TestCase):
    def setUp(self):
        self.cfg = carregar_config()
        self.contas = contas_a_receber(self.cfg)
        self.r = lista_do_dia(self.contas, date(2026, 11, 9), self.cfg)

    def test_regua(self):
        tipos = {i["id"]: i["tipo"] for i in self.r["enviar"]}
        self.assertEqual(tipos, {"1": "lembrete", "2": "vence_hoje", "3": "atraso", "4": "atraso"})

    def test_humano_sem_telefone_e_pago(self):
        self.assertEqual([i["id"] for i in self.r["humano"]], ["6"])
        self.assertEqual([i["id"] for i in self.r["sem_telefone"]], ["5"])
        self.assertNotIn("7", [i["id"] for i in self.r["enviar"] + self.r["humano"]])

    def test_link_e_tom(self):
        item = next(i for i in self.r["enviar"] if i["id"] == "3")
        self.assertTrue(item["link"].startswith("https://wa.me/5565999990003?text="))
        for proibido in ("protesto", "SPC", "Serasa", "justiça"):
            self.assertNotIn(proibido, item["mensagem"])

    def test_brl(self):
        self.assertEqual(brl(1280.5), "R$ 1.280,50")

    def test_resumo(self):
        r = resumo(self.contas, date(2026, 11, 9))
        self.assertEqual(r["vencido"], 3900 + 320 + 760 + 2100)
        self.assertEqual(r["vence_hoje"], 1280.5)
        self.assertEqual(r["vence_7d"], 450 + 5400)


if __name__ == "__main__":
    unittest.main()
