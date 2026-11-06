"""Regressões da API. Executar: python -m unittest -v test_api.

Usa SQLite temporário; nunca grava contas ou atividades no banco do projeto.
"""
import importlib
import json
import os
from pathlib import Path
import tempfile
import unittest

_previous_database = os.environ.get('EXPLORE_DATABASE_PATH')
_database = tempfile.TemporaryDirectory(prefix='explore-api-')
os.environ['EXPLORE_DATABASE_PATH'] = str(Path(_database.name) / 'test.sqlite')
backend = importlib.import_module('backend.app')
if _previous_database is None:
    os.environ.pop('EXPLORE_DATABASE_PATH', None)
else:
    os.environ['EXPLORE_DATABASE_PATH'] = _previous_database


class ExploreAPITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        backend.app.config.update(TESTING=True)

    def setUp(self):
        with backend.get_connection() as con:
            for table in ('accessibility_reports','vouchers','trip_notes','trip_shares','trip_invites','blocks','friendships','media','profiles','avaliacoes', 'historico', 'favoritos', 'roteiros_salvos', 'usuarios'):
                con.execute(f'DELETE FROM {table}')
        self.client = backend.app.test_client()
        self.trip_input = {'destination':'Raposa', 'days':2, 'budget':800,
                           'people':'2', 'transport':'Carro', 'interests':['Natureza'], 'access':[]}

    def register(self, client=None, email='ana@example.test'):
        client = client or self.client
        response = client.post('/api/auth/register', json={'name':'Ana Silva','email':email,'password':'senha-forte-123'})
        self.assertEqual(response.status_code, 201, response.json)
        return {'X-CSRF-Token':response.json['csrf']}

    def test_original_health_search_and_route(self):
        self.assertEqual(self.client.get('/api/health').status_code, 200)
        search = self.client.get('/api/destinos?q=Raposa')
        self.assertEqual(search.status_code, 200)
        self.assertGreaterEqual(search.json['total'], 1)
        route = self.client.post('/api/roteiro', json=self.trip_input)
        self.assertEqual(route.status_code, 200, route.json)
        self.assertEqual(len(route.json['days']), 2)

    def test_all_pages_and_assets(self):
        for path in ('/','/perfil','/historico','/favoritos','/meus-roteiros','/acessibilidade','/explorar','/planejar','/painel.css','/painel.js','/account.js'):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                response.close()

    def test_authentication_profile_and_persistence(self):
        headers = self.register()
        self.assertEqual(self.client.patch('/api/perfil', headers=headers, json={'name':'Ana Viajante','interests':['Praias','Cultura']}).status_code, 200)
        me = self.client.get('/api/auth/me').json['user']
        self.assertEqual(me['name'], 'Ana Viajante')
        self.assertEqual(me['interests'], ['Praias','Cultura'])
        self.assertEqual(self.client.post('/api/auth/logout', headers=headers).status_code, 200)
        self.assertIsNone(self.client.get('/api/auth/me').json['user'])
        response = self.client.post('/api/auth/login', json={'email':'ANA@example.test','password':'senha-forte-123'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['user']['name'], 'Ana Viajante')
        with backend.get_connection() as con:
            self.assertNotEqual(con.execute('SELECT senha_hash FROM usuarios').fetchone()[0], 'senha-forte-123')

    def test_authentication_and_csrf_guards(self):
        for path in ('/api/resumo','/api/historico','/api/favoritos','/api/roteiros-salvos'):
            self.assertEqual(self.client.get(path).status_code, 401)
        headers = self.register()
        self.assertEqual(self.client.delete('/api/historico').status_code, 403)
        self.assertEqual(self.client.delete('/api/historico', headers={**headers,'Origin':'https://other.test'}).status_code, 403)
        self.assertEqual(self.client.delete('/api/historico', headers=headers).status_code, 200)
        self.assertEqual(self.client.post('/api/auth/register', json={'name':'Outra Ana','email':'ANA@example.test','password':'senha-forte-123'}).status_code, 409)
        self.assertEqual(self.client.post('/api/auth/login', json={'email':'ana@example.test','password':'incorreta'}).status_code, 401)

    def test_favorites_are_idempotent_and_persistent(self):
        headers = self.register()
        place = self.client.get('/api/destinos?q=Calhau').json['results'][0]
        path = '/api/favoritos/' + str(place['id'])
        for _ in range(2):
            self.assertEqual(self.client.put(path, headers={**headers, 'Content-Type':'application/json'}).status_code, 200)
        self.assertEqual(len(self.client.get('/api/favoritos').json['results']), 1)
        history = self.client.get('/api/historico').json['results']
        self.assertEqual(sum(item['tipo']=='favorito' for item in history), 1)
        self.assertEqual(self.client.get('/api/resumo').json, {'searches':1,'favorites':1,'trips':0})
        self.assertEqual(self.client.put('/api/favoritos/99999', headers=headers).status_code, 404)
        self.assertEqual(self.client.delete(path, headers=headers).status_code, 200)
        self.assertEqual(self.client.get('/api/favoritos').json['results'], [])

    def test_saved_trips_and_user_isolation(self):
        headers = self.register()
        trip = self.client.post('/api/roteiro', headers=headers, json=self.trip_input).json
        saved = self.client.post('/api/roteiros-salvos', headers=headers, json={'title':'Fim de semana','trip':trip})
        self.assertEqual(saved.status_code, 201, saved.json)
        trip_id = saved.json['id']
        self.assertEqual(self.client.get('/api/roteiros-salvos').json['results'][0]['trip'], trip)
        self.client.put('/api/favoritos/1', headers=headers)
        other = backend.app.test_client()
        other_headers = self.register(other, 'bruno@example.test')
        self.assertEqual(other.get('/api/roteiros-salvos').json['results'], [])
        self.assertEqual(other.get('/api/favoritos').json['results'], [])
        self.assertEqual(other.get('/api/historico').json['results'], [])
        other.delete(f'/api/roteiros-salvos/{trip_id}', headers=other_headers)
        other.delete('/api/favoritos/1', headers=other_headers)
        self.assertEqual(len(self.client.get('/api/roteiros-salvos').json['results']), 1)
        self.assertEqual(len(self.client.get('/api/favoritos').json['results']), 1)
        self.client.delete(f'/api/roteiros-salvos/{trip_id}', headers=headers)
        self.assertEqual(self.client.get('/api/roteiros-salvos').json['results'], [])
        self.assertGreater(len(self.client.get('/api/historico').json['results']), 0)
        self.client.delete('/api/historico', headers=headers)
        self.assertEqual(self.client.get('/api/historico').json['results'], [])

    def test_invalid_payloads_return_json_errors(self):
        headers = self.register()
        for path in ('/api/auth/login','/api/auth/register','/api/perfil','/api/roteiro','/api/roteiros-salvos','/api/avaliacoes/1'):
            for payload in ([1], 'texto', None):
                method = 'PATCH' if path == '/api/perfil' else 'POST'
                response = self.client.open(path, method=method, headers=headers, data=json.dumps(payload), content_type='application/json')
                self.assertEqual(response.status_code, 400, (path, response.json))
                self.assertIn('error', response.json)
        for field, value in (('budget','NaN'),('budget','Infinity'),('days',0),('interests',[]),('access',None),('access',[{}])):
            response = self.client.post('/api/roteiro', headers=headers, json={**self.trip_input,field:value})
            self.assertEqual(response.status_code, 400, response.json)
        for days in ([None], [{'stops':[1]}], [{'stops':None}]):
            response = self.client.post('/api/roteiros-salvos', headers=headers, json={'trip':{'summary':{},'days':days}})
            self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.patch('/api/perfil', headers=headers, json={'name':'A','interests':[]}).status_code, 400)

    def test_reviews_and_database_integrity(self):
        headers = self.register()
        self.assertEqual(self.client.post('/api/avaliacoes/1', headers=headers, json={'rating':5,'comment':'Muito bom!'}).status_code, 200)
        self.assertEqual(self.client.post('/api/avaliacoes/1', headers=headers, json={'rating':4,'comment':'Quero voltar.'}).status_code, 200)
        self.assertEqual(len(self.client.get('/api/avaliacoes/1').json['results']), 1)
        self.assertEqual(self.client.post('/api/avaliacoes/1', headers=headers, json={'rating':7,'comment':'Muito bom!'}).status_code, 400)
        with backend.get_connection() as con:
            self.assertEqual(con.execute('PRAGMA foreign_keys').fetchone()[0], 1)
            self.assertEqual(con.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            self.assertEqual(con.execute('PRAGMA foreign_key_check').fetchall(), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
