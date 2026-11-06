"""Regressões do proxy e da configuração de produção, sem usar o banco real."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import test_api as baseline
from scripts.prepare_vercel import prepare, validate


class ProxyTest(unittest.TestCase):
    setUp = baseline.ExploreAPITest.setUp

    def test_public_origin_works_when_proxy_changes_host(self):
        with patch.object(baseline.backend, 'PUBLIC_ORIGIN', 'https://explore.example.test'):
            response = self.client.post('/api/auth/register', base_url='https://backend.example.test',
                headers={'Origin': 'https://explore.example.test'},
                json={'name': 'Teste proxy', 'email': 'proxy@example.test', 'password': 'senha-forte-123'})
            self.assertEqual(response.status_code, 201, response.json)
            csrf = response.json['csrf']
            response = self.client.patch('/api/perfil', base_url='https://backend.example.test',
                headers={'Origin': 'https://explore.example.test', 'X-CSRF-Token': csrf},
                json={'name': 'Perfil pelo proxy'})
            self.assertEqual(response.status_code, 200, response.json)

    def test_forwarded_host_cannot_authorize_foreign_origin(self):
        with patch.object(baseline.backend, 'PUBLIC_ORIGIN', 'https://explore.example.test'):
            response = self.client.post('/api/auth/login',
                headers={'Origin': 'https://evil.example.test', 'X-Forwarded-Host': 'explore.example.test'},
                json={'email': 'proxy@example.test', 'password': 'senha-forte-123'})
            self.assertEqual(response.status_code, 403)

    def test_api_and_media_are_not_cached_even_on_errors(self):
        for path in ('/api/health', '/api/auth/me', '/api/profile-settings', '/media/missing'):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).headers['Cache-Control'], 'private, no-store')


class DeploymentConfigTest(unittest.TestCase):
    def test_build_requires_real_origin_and_packages_only_marker(self):
        config = json.loads((Path(__file__).parent / 'vercel.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory(prefix='explore-build-') as directory:
            root = Path(directory)
            (root / 'vercel.json').write_text(json.dumps(config), encoding='utf-8')
            with self.assertRaises(ValueError):
                prepare(root, environ={})
            self.assertFalse((root / '.vercel/output').exists())
            prepare(root, environ={'EXPLORE_BACKEND_URL': 'https://backend.example.org'})
            output = json.loads((root / '.vercel/output/config.json').read_text(encoding='utf-8'))
            self.assertEqual(output['version'], 3)
            self.assertEqual(output['routes'][0]['dest'], 'https://backend.example.org/$1')
            self.assertEqual(list((root / '.vercel/output/static').iterdir()), [])

    def test_build_rejects_loop_to_own_vercel_domain(self):
        with tempfile.TemporaryDirectory(prefix='explore-build-') as directory:
            root = Path(directory)
            (root / 'vercel.json').write_text('{}', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'loop'):
                prepare(root, environ={'EXPLORE_BACKEND_URL': 'https://explore.vercel.app',
                                       'VERCEL_PROJECT_PRODUCTION_URL': 'explore.vercel.app'})

    def test_proxy_origin_validation(self):
        for destination in ('http://backend.example.org/:path*',
                            'https://configure-backend.invalid/:path*',
                            'https://localhost/:path*', 'https://user:pass@backend.example.org/:path*',
                            'https://backend.example.org/api/:path*'):
            with self.subTest(destination=destination), self.assertRaises(ValueError):
                validate({'rewrites': [{'source': '/:path*', 'destination': destination}]})
        validate({'rewrites': [{'source': '/:path*', 'destination': 'https://backend.example.org/:path*'}]})

    def test_production_startup_guards_and_secure_cookie(self):
        with tempfile.TemporaryDirectory(prefix='explore-deploy-') as directory:
            database = Path(directory) / 'production-test.sqlite'
            database.touch()  # Arquivo vazio exclusivamente de teste.
            env = {k: v for k, v in os.environ.items() if not k.startswith('EXPLORE_') and k != 'VERCEL'}
            env.update(EXPLORE_DATABASE_PATH=str(database), EXPLORE_PUBLIC_ORIGIN='https://explore.example.test',
                       EXPLORE_SECRET_KEY='a' * 64, EXPLORE_HTTPS='1')
            code = "from backend.app import app; c=app.test_client(); r=c.post('/api/auth/register', json={'name':'Teste','email':'prod@example.test','password':'senha-forte-123'}); assert r.status_code == 201; assert 'Secure' in r.headers['Set-Cookie']; assert not app.debug"
            result = subprocess.run([sys.executable, '-c', code], env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            for changes, message in (
                ({'EXPLORE_SECRET_KEY': ''}, 'EXPLORE_SECRET_KEY'),
                ({'EXPLORE_DATABASE_PATH': str(Path(directory) / 'missing.sqlite')}, 'EXPLORE_DATABASE_PATH'),
                ({'EXPLORE_PUBLIC_ORIGIN': 'http://explore.example.test'}, 'EXPLORE_PUBLIC_ORIGIN'),
                ({'EXPLORE_HTTPS': '0'}, 'EXPLORE_HTTPS'),
                ({'VERCEL': '1'}, 'servidor de origem'),
            ):
                with self.subTest(changes=list(changes)):
                    result = subprocess.run([sys.executable, '-c', 'import backend.app'],
                                            env={**env, **changes}, capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(message, result.stderr)


if __name__ == '__main__':
    unittest.main()
