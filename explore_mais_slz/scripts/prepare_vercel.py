"""Proxy Vercel opcional via Build Output API; não importa Flask nem abre o banco."""
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit


def validate(config):
    rule, = config['rewrites']
    destination = rule['destination']
    url = urlsplit(destination)
    if (rule['source'] != '/:path*' or url.scheme != 'https' or not url.hostname
            or url.hostname.endswith(('.invalid', '.example', '.test'))
            or url.hostname in ('localhost', '127.0.0.1', '::1')
            or url.username or url.password or url.query or url.fragment
            or url.path != '/:path*'):
        raise ValueError('Configure EXPLORE_BACKEND_URL com a origem HTTPS real do Flask, sem caminho. Para publicar em um único serviço, use render.yaml; a Vercel é opcional.')
    return destination.removesuffix('/:path*')


def prepare(root, environ=None):
    environ = os.environ if environ is None else environ
    config = json.loads((root / 'vercel.json').read_text(encoding='utf-8'))
    origin = environ.get('EXPLORE_BACKEND_URL', '').strip().rstrip('/')
    if origin:
        origin = validate({'rewrites': [{'source': '/:path*', 'destination': origin + '/:path*'}]})
    elif config.get('rewrites'):
        origin = validate(config)  # Compatibilidade com a configuração anterior.
    else:
        raise ValueError('EXPLORE_BACKEND_URL ausente. Vercel é opcional: publique diretamente com render.yaml ou informe a URL HTTPS do backend nas variáveis de build da Vercel.')
    # Recusar loop para os domínios conhecidos desta implantação.
    own_hosts = {environ.get(key, '').lower() for key in ('VERCEL_URL', 'VERCEL_PROJECT_PRODUCTION_URL')}
    if urlsplit(origin).netloc.lower() in own_hosts:
        raise ValueError('EXPLORE_BACKEND_URL aponta para a própria Vercel e causaria um loop.')
    output = root / '.vercel' / 'output'
    (output / 'static').mkdir(parents=True, exist_ok=True)
    routes = {'version': 3, 'routes': [{
        'src': '/(.*)', 'dest': origin + '/$1',
        'headers': {'Cache-Control': 'private, no-store', 'x-vercel-enable-rewrite-caching': '0'},
    }]}
    (output / 'config.json').write_text(json.dumps(routes, indent=2), encoding='utf-8')
    print('Proxy opcional gerado em .vercel/output/config.json, sem dados locais.')


if __name__ == '__main__':
    try:
        prepare(Path(__file__).resolve().parent.parent)
    except (ValueError, OSError, KeyError) as error:
        print(f'Deploy Vercel não preparado: {error}', file=sys.stderr)
        raise SystemExit(1)
