"""Entrada única e importação testadas apenas com bancos temporários."""
from contextlib import closing
import hashlib
from io import BytesIO
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from flask import Flask
from werkzeug.test import Client
from werkzeug.wrappers import Response

import test_api as baseline
from backend.hosting import HostedApplication, Settings, check_database
from scripts.backup_database import backup


class HostingTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='explore-hosting-')
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.database = self.root / 'persistent.sqlite'
        self.settings = Settings(self.database, 'https://explore.example.test', 'k' * 64, 't' * 64)
        self.loaded = []

        def loader():
            self.loaded.append(True)
            app = Flask('loaded-test-app')
            app.add_url_rule('/', 'home', lambda: 'site original')
            return app

        self.host = HostedApplication(self.settings, loader=loader)
        self.client = Client(self.host, Response)

    def fixture_bytes(self):
        path = backup(baseline.backend.DATABASE_PATH, self.root / 'upload.sqlite')
        return path.read_bytes()

    def upload(self, data, **headers):
        return self.client.post('/_hosting/import', data={'database': (BytesIO(data), 'backup.sqlite')},
                                headers={'X-Import-Token': self.settings.import_token, **headers})

    def test_initial_boot_has_no_empty_database_or_api(self):
        self.assertEqual(self.client.get('/_hosting/health').json['status'], 'waiting_for_database')
        self.assertIn('Importar seus dados', self.client.get('/').text)
        self.assertEqual(self.client.post('/api/auth/register', json={}).status_code, 503)
        self.assertFalse(self.database.exists())
        self.assertEqual(self.loaded, [])

    def test_import_authentication_origin_and_invalid_file(self):
        denied = self.client.post('/_hosting/import', data=b'not sqlite', headers={'X-Import-Token': 'wrong'})
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(self.upload(b'invalid', Origin='https://evil.example.test').status_code, 403)
        self.assertEqual(self.upload(b'not sqlite').status_code, 400)
        self.assertFalse(self.database.exists())
        self.assertEqual(list(self.root.glob('.incoming-*')), [])

    def test_import_preserves_file_and_disables_setup_permanently(self):
        content = self.fixture_bytes()
        result = self.upload(content, Origin=self.settings.public_origin)
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(self.database.read_bytes(), content)
        self.assertEqual(self.client.get('/').text, 'site original')
        self.assertEqual(self.client.get('/_hosting/health').json['status'], 'ready')
        self.assertEqual(self.upload(b'replacement').status_code, 404)
        self.assertEqual(self.database.read_bytes(), content)
        self.assertEqual(self.loaded, [True])

    def test_existing_database_cannot_be_overwritten_even_before_activation(self):
        content = self.fixture_bytes()
        self.database.write_bytes(content)
        with self.host.setup.test_client() as client:
            response = client.post('/_hosting/import', headers={'X-Import-Token': self.settings.import_token})
        self.assertEqual(response.status_code, 409)
        self.assertEqual(self.database.read_bytes(), content)

    def test_backup_preserves_original_and_blobs_and_refuses_overwrite(self):
        source = self.root / 'source.sqlite'
        content = self.fixture_bytes()
        source.write_bytes(content)
        before = hashlib.sha256(content).digest()
        with closing(sqlite3.connect(source)) as con:
            con.execute("CREATE TABLE backup_probe (data BLOB)")
            con.execute('INSERT INTO backup_probe VALUES (?)', (b'photo-bytes\x00\xff',))
            con.commit()
        before = hashlib.sha256(source.read_bytes()).digest()
        destination = backup(source, self.root / 'copied.sqlite')
        self.assertEqual(hashlib.sha256(source.read_bytes()).digest(), before)
        check_database(destination)
        with closing(sqlite3.connect(destination)) as con:
            self.assertEqual(con.execute('SELECT data FROM backup_probe').fetchone()[0], b'photo-bytes\x00\xff')
        with self.assertRaises(FileExistsError):
            backup(source, destination)
        with self.assertRaises(ValueError):
            backup(source, source)

    def test_render_configuration_uses_automatic_url_and_stable_secret(self):
        environment = {'EXPLORE_DATABASE_PATH': str(self.database),
                       'RENDER_EXTERNAL_URL': self.settings.public_origin,
                       'EXPLORE_SECRET_KEY': self.settings.secret_key,
                       'EXPLORE_IMPORT_TOKEN': self.settings.import_token, 'EXPLORE_HTTPS': '1'}
        with patch.dict(os.environ, environment, clear=True):
            self.assertEqual(Settings.from_environment(), self.settings)
        with patch.dict(os.environ, {**environment, 'EXPLORE_SECRET_KEY': ''}, clear=True):
            with self.assertRaises(ValueError):
                Settings.from_environment()

    def test_real_flask_accounts_and_images_survive_a_process_restart(self):
        self.database.write_bytes(self.fixture_bytes())
        environment = {k: v for k, v in os.environ.items() if not k.startswith('EXPLORE_') and k != 'VERCEL'}
        environment.update(EXPLORE_DATABASE_PATH=str(self.database),
                           EXPLORE_PUBLIC_ORIGIN=self.settings.public_origin,
                           EXPLORE_SECRET_KEY=self.settings.secret_key, EXPLORE_HTTPS='1',
                           TEST_STATE_PATH=str(self.root / 'test-state.json'))
        prelude = '''
from backend.hosting import HostedApplication, Settings
from werkzeug.test import Client
from werkzeug.wrappers import Response
from pathlib import Path
import os, json
c = Client(HostedApplication(Settings.from_environment()), Response)
'''
        first = '''
from PIL import Image
from io import BytesIO
r = c.post('/api/auth/register', json={'name':'Conta persistente','email':'persistent@example.test','password':'senha-forte-123'})
assert r.status_code == 201, r.text
cookie = r.headers['Set-Cookie'].split(';')[0].partition('=')[2]
csrf = r.json['csrf']
image = BytesIO(); Image.new('RGB', (20,20), 'green').save(image, format='PNG'); image.seek(0)
r = c.post('/api/profile-media/avatar', data={'image':(image, 'photo.png')}, headers={'X-CSRF-Token':csrf})
assert r.status_code == 201, r.text
Path(os.environ['TEST_STATE_PATH']).write_text(json.dumps({'cookie':cookie,'media':r.json['url']}))
'''
        second = '''
state = json.loads(Path(os.environ['TEST_STATE_PATH']).read_text())
c.set_cookie('session', state['cookie'])
assert c.get('/api/auth/me').json['user']['name'] == 'Conta persistente'
r = c.get(state['media']); assert r.status_code == 200 and r.mimetype == 'image/jpeg'
assert c.get('/_hosting/health').json['status'] == 'ready'
assert c.post('/_hosting/import').status_code in (404, 405)
'''
        for code in (first, second):
            result = subprocess.run([sys.executable, '-c', prelude + code], env=environment,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
