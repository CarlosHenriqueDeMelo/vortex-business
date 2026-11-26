"""Testes basicos da API. Rodar: cd backend && python -m unittest discover tests"""
import os, sys, tempfile, unittest

os.environ['HOME'] = tempfile.mkdtemp()           # Linux/macOS
os.environ['APPDATA'] = os.environ['HOME']        # Windows
os.environ['VORTEX_SYNC_TOKEN'] = 'teste123'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app  # noqa: E402

LOCAL = {'REMOTE_ADDR': '127.0.0.1'}
REDE = {'REMOTE_ADDR': '192.168.0.9'}
TOKEN = {'X-Sync-Token': 'teste123'}


class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = app.test_client()
        r = cls.c.post('/empresas', json={'nome': 'Loja', 'senha': '1234', 'pergunta_seguranca': 'Cor?',
                                          'resposta_seguranca': 'Azul'}, environ_overrides=LOCAL)
        assert r.status_code == 201

    def test_login_e_bloqueio(self):
        ok = self.c.post('/empresas/login', json={'id': 1, 'senha': '1234'}, environ_overrides=LOCAL)
        self.assertEqual(ok.status_code, 200)
        for _ in range(5):
            self.c.post('/empresas/login', json={'id': 1, 'senha': '0000'}, environ_overrides=LOCAL)
        self.assertEqual(self.c.post('/empresas/login', json={'id': 1, 'senha': '1234'},
                                     environ_overrides=LOCAL).status_code, 429)

    def test_rede_so_acessa_sync(self):
        self.assertEqual(self.c.get('/produtos', environ_overrides=REDE).status_code, 403)
        self.assertEqual(self.c.get('/sync/empresas', environ_overrides=REDE).status_code, 401)
        self.assertEqual(self.c.get('/sync/empresas', headers=TOKEN, environ_overrides=REDE).status_code, 200)

    def test_sync_traduz_relacoes(self):
        push = {'empresa_id': 1, 'dados': {
            'produtos': [{'uuid': 'p1', 'updated_at': '2026-01-01 10:00:00', 'empresa_id': 1, 'nome': 'A', 'quantidade': 5}],
            'vendas': [{'uuid': 'v1', 'updated_at': '2026-01-01 10:00:00', 'empresa_id': 1, 'forma_pagamento': 'Pix', 'total': 5}],
            'itens_venda': [{'uuid': 'i1', 'updated_at': '2026-01-01 10:00:00', 'venda_id': 'v1', 'produto_id': 'p1',
                             'quantidade': 1, 'preco_unitario': 5, 'subtotal': 5}]}}
        r = self.c.post('/sync/push', json=push, headers=TOKEN, environ_overrides=REDE)
        self.assertEqual(r.status_code, 200)
        pull = self.c.get('/sync/pull?empresa_id=1', headers=TOKEN, environ_overrides=REDE).json
        item = [i for i in pull['itens_venda'] if i['uuid'] == 'i1'][0]
        self.assertEqual((item['venda_id'], item['produto_id']), ('v1', 'p1'))

    def test_venda_sem_itens(self):
        r = self.c.post('/vendas', json={'empresa_id': 1, 'forma_pagamento': 'Pix', 'total': 1, 'itens': []},
                        environ_overrides=LOCAL)
        self.assertEqual(r.status_code, 400)


if __name__ == '__main__':
    unittest.main()
