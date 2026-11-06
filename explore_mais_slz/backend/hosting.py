"""Entrada de produção: importa o SQLite uma única vez e serve todo o site."""
from dataclasses import dataclass
from contextlib import closing
import importlib
import os
from pathlib import Path
import secrets
import sqlite3
import tempfile
from threading import Lock
from urllib.parse import urlsplit

from flask import Flask, jsonify, request
from werkzeug.wrappers import Response


REQUIRED_TABLES = {
    'destinos', 'usuarios', 'historico', 'favoritos', 'roteiros_salvos', 'avaliacoes',
    'schema_migrations', 'profiles', 'media', 'friendships', 'blocks', 'trip_invites',
    'trip_notes', 'trip_shares', 'vouchers', 'accessibility_reports',
}


def check_database(path):
    """Somente leitura: não cria arquivo, não importa app.py nem migra esquema."""
    with closing(sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True)) as connection:
        if connection.execute('PRAGMA quick_check').fetchall() != [('ok',)]:
            raise ValueError('O arquivo não passou na verificação de integridade SQLite.')
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not REQUIRED_TABLES <= tables:
            raise ValueError('Selecione um backup completo do Explore+ SLZ, incluindo perfis e imagens.')
        if not connection.execute('SELECT 1 FROM schema_migrations WHERE version=2').fetchone():
            raise ValueError('O esquema precisa ser preparado separadamente; a importação não executa migrações.')
        if connection.execute('PRAGMA foreign_key_check').fetchone():
            raise ValueError('Existem referências inválidas no banco; preserve o original e revise o backup.')


@dataclass(frozen=True)
class Settings:
    database: Path
    public_origin: str
    secret_key: str
    import_token: str

    @classmethod
    def from_environment(cls):
        path = Path(os.environ.get('EXPLORE_DATABASE_PATH', ''))
        origin = (os.environ.get('EXPLORE_PUBLIC_ORIGIN') or os.environ.get('RENDER_EXTERNAL_URL', '')).rstrip('/')
        url = urlsplit(origin)
        if (url.scheme != 'https' or not url.netloc or url.username or url.password
                or url.path or url.query or url.fragment):
            raise ValueError('Defina uma origem HTTPS em EXPLORE_PUBLIC_ORIGIN ou use a URL automática do Render.')
        if not path.is_absolute() or not path.parent.is_dir():
            raise ValueError('EXPLORE_DATABASE_PATH deve apontar para um diretório persistente já montado.')
        key = os.environ.get('EXPLORE_SECRET_KEY', '')
        token = os.environ.get('EXPLORE_IMPORT_TOKEN', '')
        if len(key) < 32 or os.environ.get('EXPLORE_HTTPS') != '1':
            raise ValueError('Configure EXPLORE_SECRET_KEY estável e EXPLORE_HTTPS=1.')
        if not path.exists() and len(token) < 32:
            raise ValueError('O primeiro envio requer EXPLORE_IMPORT_TOKEN aleatório de pelo menos 32 caracteres.')
        return cls(path, origin, key, token)


SETUP_HTML = '''<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Preparar Explore+ SLZ</title>
<style>body{font:17px system-ui;max-width:620px;margin:10vh auto;padding:24px;color:#183d32}
label,input,button{display:block;margin:16px 0}input{max-width:100%;padding:8px}button{padding:12px;cursor:pointer}</style>
<h1>Importar seus dados</h1>
<p>Envie a cópia de segurança do Explore+ SLZ. Ela inclui contas, perfis e imagens.
O site será liberado após o envio. Nenhum banco vazio será criado.</p>
<form id="upload"><label>Chave de importação
<input id="token" type="password" required autocomplete="off"></label>
<label>Cópia SQLite (até 64 MB)<input id="database" type="file" accept=".sqlite,.sqlite3,.db" required></label>
<button>Enviar cópia e abrir o site</button></form><p id="result" role="status"></p>
<script>document.querySelector('#upload').onsubmit=async event=>{
event.preventDefault();const button=document.querySelector('button'),result=document.querySelector('#result');
button.disabled=true;result.textContent='Verificando e enviando…';
try{const data=new FormData();data.append('database',document.querySelector('#database').files[0]);
const response=await fetch('/_hosting/import',{method:'POST',headers:{'X-Import-Token':document.querySelector('#token').value},body:data});
const payload=await response.json();if(!response.ok)throw Error(payload.error||'Falha no envio.');
location.replace('/');}catch(error){result.textContent=error.message;button.disabled=false;}};</script></html>'''


class HostedApplication:
    def __init__(self, settings, loader=None):
        self.settings = settings
        self.lock = Lock()
        self.application = None
        self.loader = loader or self.load_flask
        self.setup = Flask('explore_first_import', static_folder=None)
        self.setup.config['MAX_CONTENT_LENGTH'] = 65 * 1024 * 1024
        self.setup.add_url_rule('/', 'setup', lambda: SETUP_HTML)
        self.setup.add_url_rule('/_hosting/import', 'import', self.import_database, methods=['POST'])

        @self.setup.errorhandler(413)
        def too_large(error):
            return jsonify(error='A cópia pode ter até 64 MB.'), 413

        @self.setup.after_request
        def private(response):
            response.headers['Cache-Control'] = 'private, no-store'
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['Referrer-Policy'] = 'no-referrer'
            response.headers['X-Frame-Options'] = 'DENY'
            return response

    def load_flask(self):
        check_database(self.settings.database)
        os.environ['EXPLORE_DATABASE_PATH'] = str(self.settings.database)
        os.environ['EXPLORE_PUBLIC_ORIGIN'] = self.settings.public_origin
        os.environ['EXPLORE_SECRET_KEY'] = self.settings.secret_key
        os.environ['EXPLORE_HTTPS'] = '1'
        return importlib.import_module('backend.app').app

    def import_database(self):
        # Autenticar antes de ler o corpo; a chave nunca passa pela URL ou pelo Git.
        token = request.headers.get('X-Import-Token', '')
        if not self.settings.import_token or not secrets.compare_digest(token.encode(), self.settings.import_token.encode()):
            return jsonify(error='Chave de importação inválida.'), 403
        origin = request.headers.get('Origin')
        if origin and origin.rstrip('/') != self.settings.public_origin:
            return jsonify(error='Origem não autorizada.'), 403
        with self.lock:
            if self.settings.database.exists():
                return jsonify(error='Já existe um banco. A importação não pode substituí-lo.'), 409
            upload = request.files.get('database')
            if not upload:
                return jsonify(error='Selecione a cópia SQLite.'), 400
            descriptor, name = tempfile.mkstemp(prefix='.incoming-', suffix='.sqlite', dir=self.settings.database.parent)
            incoming = Path(name)
            try:
                size = 0
                with os.fdopen(descriptor, 'wb') as output:
                    while chunk := upload.stream.read(1024 * 1024):
                        size += len(chunk)
                        if size > 64 * 1024 * 1024:
                            return jsonify(error='A cópia pode ter até 64 MB.'), 413
                        output.write(chunk)
                    output.flush()
                    os.fsync(output.fileno())
                check_database(incoming)
                # Publicação atômica sem sobrescrita, inclusive em requisições concorrentes.
                os.link(incoming, self.settings.database)
                return jsonify(ok=True)
            except FileExistsError:
                return jsonify(error='Já existe um banco. Nenhum dado foi substituído.'), 409
            except (ValueError, sqlite3.DatabaseError) as error:
                return jsonify(error='Cópia inválida. ' + str(error)), 400
            finally:
                incoming.unlink(missing_ok=True)  # Apenas o temporário criado por este envio.

    def __call__(self, environ, start_response):
        with self.lock:
            if self.application is None and self.settings.database.is_file():
                self.application = self.loader()
        if environ.get('PATH_INFO') == '/_hosting/health':
            state = 'ready' if self.application else 'waiting_for_database'
            return Response(jsonify_status(state), mimetype='application/json', headers={'Cache-Control': 'no-store'})(environ, start_response)
        if self.application is not None:
            return self.application(environ, start_response)
        if environ.get('PATH_INFO', '').startswith('/api/'):
            return Response('{"error":"Aguardando importação do banco."}', status=503,
                            mimetype='application/json', headers={'Cache-Control': 'no-store'})(environ, start_response)
        return self.setup(environ, start_response)


def jsonify_status(state):
    import json
    return json.dumps({'status': state})


def main():
    from waitress import serve
    application = HostedApplication(Settings.from_environment())
    serve(application, host='0.0.0.0', port=int(os.environ.get('PORT', '8000')),
          max_request_body_size=65 * 1024 * 1024)


if __name__ == '__main__':
    main()
