"""Regressões de segurança e persistência da expansão, com SQLite temporário."""
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
from io import BytesIO
import json
from pathlib import Path
import sqlite3
import tempfile
import os
import subprocess
import sys
import unittest
from PIL import Image
import test_api as baseline
from backend.migrations import migrate, ACCESS_FIELDS
from backend.catalog import seed_catalog, GROUPS

backend=baseline.backend


class ExpansionAPITest(unittest.TestCase):
    setUp=baseline.ExploreAPITest.setUp
    register=baseline.ExploreAPITest.register

    def new_user(self,email,handle):
        client=backend.app.test_client(); headers=self.register(client,email)
        response=client.patch('/api/profile-settings',headers=headers,json={'handle':handle,'discoverable':True})
        self.assertEqual(response.status_code,200,response.json)
        return client,headers,client.get('/api/auth/me').json['user']['id']

    def pair(self):
        a,ah,aid=self.new_user('alice@example.test','alice')
        b,bh,bid=self.new_user('bruno@example.test','bruno')
        self.assertEqual(a.post(f'/api/friends/{bid}',headers=ah,json={'action':'request'}).status_code,200)
        self.assertEqual(b.post(f'/api/friends/{aid}',headers=bh,json={'action':'accept'}).status_code,200)
        return a,ah,aid,b,bh,bid

    def save(self,client,headers):
        trip=client.post('/api/roteiro',headers=headers,json=self.trip_input).json
        return client.post('/api/roteiros-salvos',headers=headers,json={'title':'Passeio em companhia','trip':trip}).json['id']

    def test_catalog_sources_idempotency_and_filters(self):
        data=self.client.get('/api/destinos').json
        self.assertGreaterEqual(len([d for d in data['results'] if d['source_url']]),60)
        self.assertEqual(len(data['results']),len({d['name'] for d in data['results']}))
        expected=len(data['results']);seed_catalog(backend.get_connection)
        self.assertEqual(self.client.get('/api/destinos').json['total'],expected)
        search=self.client.get('/api/destinos?q=SAO LUIS&municipality=São Luís&category=Museu').json
        self.assertGreater(search['total'],0)
        self.assertTrue(all(d['category']=='Museu' and d['municipality']=='São Luís' for d in search['results']))
        place=data['results'][0]; response=self.client.get(f"/api/destinos/{place['id']}")
        self.assertEqual(response.status_code,200)
        self.assertTrue(all(v['status']=='unverified' for v in response.json['destination']['accessibility'].values()))
        self.assertEqual(self.client.get('/api/destinos?access=mobility').json['total'],0)
        self.assertEqual(self.client.get('/api/destinos?access=invalid').status_code,400)
        # The seed must never replace an operator's correction.
        with backend.get_connection() as con:
            previous=con.execute('SELECT descricao FROM destinos WHERE id=?',(place['id'],)).fetchone()[0]
            con.execute('UPDATE destinos SET descricao=? WHERE id=?',('Correção manual de teste',place['id']))
        try:
            seed_catalog(backend.get_connection)
            self.assertEqual(self.client.get(f"/api/destinos/{place['id']}").json['destination']['description'],'Correção manual de teste')
        finally:
            with backend.get_connection() as con:con.execute('UPDATE destinos SET descricao=? WHERE id=?',(previous,place['id']))

    def test_profile_defaults_handle_and_consent(self):
        a,headers,aid=self.new_user('alice@example.test','alice')
        p=a.get('/api/profile-settings').json['profile']
        self.assertFalse(p['is_public']);self.assertEqual(p['favorites_visibility'],'private')
        self.assertEqual(backend.app.test_client().get('/api/public-profile/alice').status_code,404)
        response=a.patch('/api/profile-settings',headers=headers,json={'access_preferences':['visual'],'access_consent':False})
        self.assertEqual(response.json['profile']['access_preferences'],[])
        response=a.patch('/api/profile-settings',headers=headers,json={'access_preferences':['visual'],'access_consent':True,'is_public':True,'bio':'Minha história','avatar_x':75})
        self.assertEqual(response.status_code,200,response.json)
        public=backend.app.test_client().get('/api/public-profile/alice').json['profile']
        for key in ('email','access_preferences','access_consent','historico'):self.assertNotIn(key,public)
        self.assertIsNone(public['favorites'])
        b,bh,_=self.new_user('b@example.test','bruno')
        self.assertEqual(b.patch('/api/profile-settings',headers=bh,json={'handle':'ALICE'}).status_code,409)
        for data in ({'handle':'a/b'},{'avatar_x':101},{'is_public':'true'},{'access_preferences':['invalid']}):
            self.assertEqual(a.patch('/api/profile-settings',headers=headers,json=data).status_code,400)
        self.assertEqual(a.patch('/api/profile-settings',json={'bio':'sem token'}).status_code,403)

    def test_upload_content_limits_privacy_and_removal(self):
        a,ah,aid=self.new_user('alice@example.test','alice')
        output=BytesIO();Image.new('RGB',(40,40),'green').save(output,format='PNG');png=output.getvalue()
        response=a.post('/api/profile-media/avatar',headers=ah,data={'image':(BytesIO(png),'../../arquivo.html')},content_type='multipart/form-data')
        self.assertEqual(response.status_code,201,response.json);url=response.json['url']
        self.assertNotIn('arquivo',url)
        own=a.get(url);self.assertEqual(own.status_code,200);self.assertEqual(own.mimetype,'image/jpeg');self.assertEqual(own.headers['X-Content-Type-Options'],'nosniff')
        self.assertEqual(backend.app.test_client().get(url).status_code,404)
        a.patch('/api/profile-settings',headers=ah,json={'is_public':True})
        self.assertEqual(backend.app.test_client().get(url).status_code,200)
        for payload in (b'<svg onload="alert(1)"></svg>',b'not an image',png[:20]):
            self.assertEqual(a.post('/api/profile-media/avatar',headers=ah,data={'image':(BytesIO(payload),'imagem.png')}).status_code,400)
        oversized=a.post('/api/profile-media/cover',headers=ah,data={'image':(BytesIO(b'x'*(4*1024*1024+1)),'large.jpg')})
        self.assertEqual(oversized.status_code,413)
        oversized.request.input_stream.close()
        oversized.close()
        self.assertEqual(backend.app.test_client().post('/api/profile-media/avatar',data={'image':(BytesIO(png),'a.png')}).status_code,401)
        self.assertEqual(a.delete('/api/profile-media/avatar',headers=ah).status_code,200)
        self.assertEqual(a.get(url).status_code,404)

    def test_people_search_does_not_expose_private_data(self):
        a,ah,aid=self.new_user('alice@example.test','alice')
        b,bh,bid=self.new_user('bruno@example.test','bruno')
        result=a.get('/api/people?q=bruno').json['results']
        self.assertEqual(result[0]['id'],bid)
        for key in ('email','bio','access_preferences'):self.assertNotIn(key,result[0])
        b.patch('/api/profile-settings',headers=bh,json={'discoverable':False})
        self.assertEqual(a.get('/api/people?q=bruno').json['results'],[])
        self.assertEqual(a.post(f'/api/friends/{bid}',headers=ah,json={'action':'request'}).status_code,403)
        self.assertEqual(a.post(f'/api/friends/{aid}',headers=ah,json={'action':'request'}).status_code,400)

    def test_friend_rejection_removal_block_and_unblock(self):
        a,ah,aid=self.new_user('alice@example.test','alice');b,bh,bid=self.new_user('bruno@example.test','bruno')
        a.post(f'/api/friends/{bid}',headers=ah,json={'action':'request'})
        self.assertEqual(a.post(f'/api/friends/{bid}',headers=ah,json={'action':'accept'}).status_code,409)
        b.post(f'/api/friends/{aid}',headers=bh,json={'action':'reject'})
        self.assertEqual(b.get('/api/friends').json['results'],[])
        a.post(f'/api/friends/{bid}',headers=ah,json={'action':'request'});b.post(f'/api/friends/{aid}',headers=bh,json={'action':'accept'})
        self.assertEqual(a.get('/api/profile-settings').json['profile']['friend_count'],1)
        self.assertEqual(a.post(f'/api/friends/{bid}',headers=ah,json={'action':'request'}).status_code,409)
        a.post(f'/api/friends/{bid}',headers=ah,json={'action':'remove'})
        self.assertEqual(b.get('/api/friends').json['results'],[])
        a.post(f'/api/friends/{bid}',headers=ah,json={'action':'block'})
        self.assertEqual(b.get('/api/people?q=alice').json['results'],[])
        self.assertEqual(b.get('/api/public-profile/alice').status_code,404)
        self.assertEqual(b.post(f'/api/friends/{aid}',headers=bh,json={'action':'request'}).status_code,404)
        a.post(f'/api/friends/{bid}',headers=ah,json={'action':'unblock'})
        self.assertEqual(a.get('/api/friends').json['results'],[])

    def test_favorites_visibility_and_history_privacy(self):
        a,ah,aid,b,bh,bid=self.pair();a.put('/api/favoritos/1',headers=ah)
        a.patch('/api/profile-settings',headers=ah,json={'favorites_visibility':'friends'})
        self.assertEqual(len(b.get('/api/public-profile/alice').json['profile']['favorites']),1)
        self.assertEqual(backend.app.test_client().get('/api/public-profile/alice').status_code,404)
        a.patch('/api/profile-settings',headers=ah,json={'is_public':True,'favorites_visibility':'public'})
        self.assertEqual(len(backend.app.test_client().get('/api/public-profile/alice').json['profile']['favorites']),1)
        self.assertEqual(b.get('/api/historico').json['results'],[])
        a.post(f'/api/friends/{bid}',headers=ah,json={'action':'block'})
        self.assertEqual(b.get('/api/public-profile/alice').status_code,404)

    def test_trip_invitation_collaboration_and_link_revocation(self):
        a,ah,aid,b,bh,bid=self.pair();trip_id=self.save(a,ah)
        self.assertEqual(b.get(f'/api/trips/{trip_id}').status_code,403)
        self.assertEqual(a.post(f'/api/trips/{trip_id}/invites',headers=ah,json={'recipient_id':bid}).status_code,201)
        invite=b.get('/api/trip-invites').json['results'][0]['id']
        self.assertEqual(b.get(f'/api/trips/{trip_id}').status_code,403)
        self.assertEqual(b.post(f'/api/trip-invites/{invite}',headers=bh,json={'action':'accept'}).status_code,200)
        self.assertEqual(b.patch(f'/api/trips/{trip_id}',headers=bh,json={'title':'Título do grupo'}).status_code,200)
        self.assertEqual(b.post(f'/api/trips/{trip_id}/notes',headers=bh,json={'text':'Vamos confirmar o transporte.'}).status_code,201)
        self.assertEqual(len(a.get(f'/api/trips/{trip_id}').json['notes']),1)
        self.assertEqual(b.post(f'/api/trips/{trip_id}/share',headers=bh).status_code,403)
        url=a.post(f'/api/trips/{trip_id}/share',headers=ah).json['url']
        anonymous=backend.app.test_client();public=anonymous.get('/api/shared/'+url.split('/')[-1])
        self.assertEqual(public.status_code,200);self.assertNotIn('notes',public.json)
        a.delete(f'/api/trips/{trip_id}/share',headers=ah)
        self.assertEqual(anonymous.get('/api/shared/'+url.split('/')[-1]).status_code,404)
        a.post(f'/api/friends/{bid}',headers=ah,json={'action':'block'})
        self.assertEqual(b.get(f'/api/trips/{trip_id}').status_code,404)

    def test_viewer_permission_and_declined_invites(self):
        a,ah,aid,b,bh,bid=self.pair();trip_id=self.save(a,ah)
        a.post(f'/api/trips/{trip_id}/invites',headers=ah,json={'recipient_id':bid,'role':'viewer'})
        invite=b.get('/api/trip-invites').json['results'][0]['id']
        b.post(f'/api/trip-invites/{invite}',headers=bh,json={'action':'reject'})
        self.assertEqual(b.get(f'/api/trips/{trip_id}').status_code,403)
        a.post(f'/api/trips/{trip_id}/invites',headers=ah,json={'recipient_id':bid,'role':'viewer'})
        b.post(f'/api/trip-invites/{invite}',headers=bh,json={'action':'accept'})
        self.assertEqual(b.get(f'/api/trips/{trip_id}').status_code,200)
        self.assertEqual(b.post(f'/api/trips/{trip_id}/notes',headers=bh,json={'text':'Sem permissão'}).status_code,403)
        self.assertEqual(b.patch(f'/api/trips/{trip_id}',headers=bh,json={'title':'Não pode'}).status_code,403)
        a.post(f'/api/trip-invites/{invite}',headers=ah,json={'action':'revoke'})
        self.assertEqual(b.get(f'/api/trips/{trip_id}').status_code,403)

    def test_voucher_lifecycle_and_ownership(self):
        a,ah,aid,b,bh,bid=self.pair();c,ch,cid=self.new_user('carol@example.test','carol')
        payload={'recipient_id':bid,'destination_id':1,'message':'Vamos juntos!','theme':'azulejo','expires_at':(datetime.now(timezone.utc)+timedelta(days=10)).date().isoformat()}
        response=a.post('/api/vouchers',headers=ah,json=payload);self.assertEqual(response.status_code,201,response.json);voucher=response.json['id']
        self.assertEqual(b.get('/api/vouchers').json['results'],[])
        self.assertEqual(c.post(f'/api/vouchers/{voucher}/transition',headers=ch,json={'action':'redeem'}).status_code,404)
        self.assertEqual(a.post(f'/api/vouchers/{voucher}/transition',headers=ah,json={'action':'redeem'}).status_code,409)
        self.assertEqual(a.post(f'/api/vouchers/{voucher}/transition',headers=ah,json={'action':'send'}).status_code,200)
        self.assertEqual(len(b.get('/api/vouchers').json['results']),1)
        self.assertEqual(b.post(f'/api/vouchers/{voucher}/transition',headers=bh,json={'action':'redeem'}).status_code,200)
        self.assertEqual(b.post(f'/api/vouchers/{voucher}/transition',headers=bh,json={'action':'redeem'}).status_code,409)
        self.assertEqual(a.post(f'/api/vouchers/{voucher}/transition',headers=ah,json={'action':'cancel'}).status_code,409)
        self.assertEqual(a.get('/api/vouchers').json['results'][0]['status'],'redeemed')

    def test_voucher_expiration_cancellation_and_block(self):
        a,ah,aid,b,bh,bid=self.pair();payload={'recipient_id':bid,'destination_id':1,'expires_at':(datetime.now(timezone.utc)+timedelta(days=2)).date().isoformat()}
        first=a.post('/api/vouchers',headers=ah,json=payload).json['id']
        self.assertEqual(a.post(f'/api/vouchers/{first}/transition',headers=ah,json={'action':'cancel'}).status_code,200)
        second=a.post('/api/vouchers',headers=ah,json=payload).json['id']
        with backend.get_connection() as con:con.execute("UPDATE vouchers SET expires_at='2000-01-01T00:00:00+00:00' WHERE id=?",(second,))
        self.assertEqual(a.get('/api/vouchers').json['results'][0]['status'],'expired')
        self.assertEqual(a.post(f'/api/vouchers/{second}/transition',headers=ah,json={'action':'send'}).status_code,409)
        third=a.post('/api/vouchers',headers=ah,json=payload).json['id']
        a.post(f'/api/vouchers/{third}/transition',headers=ah,json={'action':'send'})
        b.post(f'/api/friends/{aid}',headers=bh,json={'action':'block'})
        self.assertEqual(a.get('/api/vouchers').json['results'][0]['status'],'cancelled')
        self.assertEqual(a.post('/api/vouchers',headers=ah,json=payload).status_code,403)

    def test_accessibility_reports_do_not_self_publish(self):
        a,ah,aid=self.new_user('alice@example.test','alice')
        payload={'destination_id':1,'feature':'ramp','proposed_status':'confirmed','description':'Informação de teste a ser verificada.'}
        response=a.post('/api/accessibility-reports',headers=ah,json=payload)
        self.assertEqual(response.status_code,201,response.json)
        self.assertEqual(response.json['status'],'pending')
        self.assertEqual(a.get('/api/destinos/1').json['destination']['accessibility']['ramp']['status'],'unverified')
        self.assertEqual(a.post('/api/roteiro',headers=ah,json={**self.trip_input,'access':['Mobilidade reduzida']}).status_code,422)
        # Only an explicit, evidenced resource can satisfy its own filter; no group is inferred.
        with backend.get_connection() as con:con.execute('UPDATE destinos SET access_json=? WHERE id=1',(json.dumps({'ramp':{'status':'confirmed','source_url':'https://evidence.example.test','verified_at':'2026-11-06'}}),))
        try:
            self.assertEqual(a.get('/api/destinos?access=ramp').json['total'],1)
            self.assertEqual(a.get('/api/destinos?access=mobility').json['total'],0)
        finally:
            with backend.get_connection() as con:con.execute("UPDATE destinos SET access_json='{}' WHERE id=1")
        self.assertEqual(a.post('/api/accessibility-reports',headers=ah,json={**payload,'feature':'invalid'}).status_code,400)

    def test_themes_and_new_pages(self):
        for theme in ('reggae','quilombo','sabores','historia','popular'):
            response=self.client.post('/api/roteiro',json={**self.trip_input,'destination':'São Luís','theme':theme})
            self.assertEqual(response.status_code,200,(theme,response.json))
            if theme=='quilombo':self.assertTrue(all('Quilombo' in s['name'] or 'Liberdade' in s['name'] or 'Floresta' in s['name'] for d in response.json['days'] for s in d['stops']))
        for path in ('/catalogo','/cultura','/amigos','/presentes','/configuracoes','/destino/1','/p/alice','/s/none'):
            response=self.client.get(path,follow_redirects=True);self.assertEqual(response.status_code,200,path);response.close()

    def test_local_moderation_workflow(self):
        a,ah,_=self.new_user('moderation@example.test','moderation')
        payload={'destination_id':1,'feature':'ramp','proposed_status':'confirmed','description':'Evidência de teste isolada, sem publicação real.'}
        report=a.post('/api/accessibility-reports',headers=ah,json=payload).json['id']
        environment={**os.environ,'EXPLORE_DATABASE_PATH':str(backend.DATABASE_PATH)}
        result=subprocess.run([sys.executable,'-m','backend.moderate_accessibility','approve',str(report),'--source','https://evidence.example.test','--date',datetime.now(timezone.utc).date().isoformat(),'--reviewer','Teste'],env=environment,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        try:
            self.assertEqual(a.get('/api/destinos/1').json['destination']['accessibility']['ramp']['status'],'confirmed')
            self.assertEqual(a.get('/api/accessibility-reports').json['results'][0]['status'],'approved')
        finally:
            with backend.get_connection() as con:con.execute("UPDATE destinos SET access_json='{}' WHERE id=1")

    def test_migration_preserves_legacy_data_and_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'legacy.sqlite'
            @contextmanager
            def connect():
                con=sqlite3.connect(path);con.row_factory=sqlite3.Row
                try:
                    with con:yield con
                finally:con.close()
            with connect() as con:
                con.executescript('''CREATE TABLE destinos (id INTEGER PRIMARY KEY,nome TEXT UNIQUE,municipio TEXT,descricao TEXT,icone TEXT,interesses TEXT,latitude REAL,longitude REAL);
                CREATE TABLE usuarios (id INTEGER PRIMARY KEY,nome TEXT);
                CREATE TABLE favoritos (usuario_id INTEGER,destino_id INTEGER);
                INSERT INTO usuarios VALUES (42,'Pessoa existente');
                INSERT INTO destinos VALUES (88,'Local manual','São Luís','Texto manual','x','[]',NULL,NULL);
                INSERT INTO favoritos VALUES (42,88);''')
            migrate(connect,path);migrate(connect,path);seed_catalog(connect)
            with connect() as con:
                self.assertEqual(con.execute('SELECT nome FROM usuarios WHERE id=42').fetchone()[0],'Pessoa existente')
                self.assertEqual(con.execute('SELECT descricao FROM destinos WHERE id=88').fetchone()[0],'Texto manual')
                self.assertEqual(tuple(con.execute('SELECT * FROM favoritos').fetchone()),(42,88))
                self.assertEqual(con.execute('SELECT COUNT(*) FROM schema_migrations WHERE version=2').fetchone()[0],1)
            backups=list((Path(directory)/'backups').glob('*.sql'))
            self.assertEqual(len(backups),1);self.assertNotIn('Pessoa existente',backups[0].read_text(encoding='utf-8'))


if __name__=='__main__':unittest.main(verbosity=2)
