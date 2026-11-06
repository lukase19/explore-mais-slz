"""Valida a origem antes do build do proxy. Não importa Flask nem abre o banco."""
import json
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
        raise ValueError('Defina em vercel.json a origem HTTPS real do Flask: https://seu-backend/:path*. Não use a URL pública da própria Vercel (loop).')


def prepare(root):
    config = json.loads((root / 'vercel.json').read_text(encoding='utf-8'))
    validate(config)
    # Nenhuma página local: todas as rotas, inclusive /, são encaminhadas ao Flask.
    output = root / config['outputDirectory']
    output.mkdir(exist_ok=True)
    # A saída precisa conter um arquivo. Não há index.html que substitua o Flask.
    (output / 'proxy-ready.txt').write_text('Explore+ SLZ reverse proxy\n', encoding='utf-8')
    print('Configuração do proxy validada. Nenhum dado local foi empacotado.')


if __name__ == '__main__':
    prepare(Path(__file__).resolve().parent.parent)
